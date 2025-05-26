import os
import logging

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from fpdf import FPDF
from datetime import timedelta
from concurrent.futures import ProcessPoolExecutor, as_completed

from nappa.objects import SleepRecording
from isa.core.plots import make_main_fig, make_bar_fig, make_violin_fig, make_donut_fig
from isa.core.wear import detect_wear_blocks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sleep_statistics(
    recording: SleepRecording,
    wear_idx: pd.Series,
) -> dict:
    """
    Calculate sleep statistics from a given SleepRecording object.
    Parameters:
    recording : SleepRecording
        The sleep recording object to analyze.
    wear_idx : array-like of bool
        A boolean mask indicating the wear time indexes.
    Returns:
    dict : A dictionary containing the following sleep statistics:
        - nonwear_time: Total non-wear time.
        - awake_time: Total awake time.
        - light_sleep: Total light sleep time.
        - deep_sleep: Total deep sleep time.
        - total_sleep: Total sleep time.
        - total_time: Total recording time.
        - awakenings: Number of awakenings.
    """
    total_time = recording.duration
    stage_counts = recording.labels.loc[wear_idx, 'sleep_stage'].value_counts()
    awakenings = 0

    awake_time   = timedelta(seconds=stage_counts.get('wake', 0) * 30.0)
    light_sleep  = timedelta(seconds=stage_counts.get('light', 0) * 30.0)
    deep_sleep   = timedelta(seconds=stage_counts.get('deep', 0) * 30.0)
    nonwear_time = timedelta(seconds=np.sum(~wear_idx) * 30.0)
    total_sleep = light_sleep + deep_sleep

    for i, (idx, row) in enumerate(recording.labels.iterrows()):
        if row['sleep_stage'] == 'wake':
            if recording.labels.iloc[i-1]['sleep_stage'] != 'wake':
                awakenings += 1

    return dict({ 'nonwear_time': nonwear_time, 'awake_time': awake_time,
                  'light_sleep' : light_sleep,  'deep_sleep': deep_sleep,
                  'total_sleep' : total_sleep,  'total_time': total_time,
                  'awakenings'  : awakenings })



def _render_subpage(args) -> tuple:
    """
    Worker process: render the figures for ONE sleep-period page,
    write them as PNGs into tmp_dir, and return everything the parent
    needs to finish the PDF page.
    """
    (idx, period, recording, wear_idx, settings, tmp_dir) = args

    sleep_period = SleepRecording(
        features=recording.features.loc[period[0]:period[1]],
        labels  =recording.labels.loc[period[0]:period[1]]
    )
    sub_wear_idx = wear_idx.loc[period[0]:period[1]]

    # ── main timeline figure ───────────────────────────────
    main_fig, _ = make_main_fig(
        sleep_period, sub_wear_idx, settings, isMainPage=False)
    main_png = os.path.join(tmp_dir, f"main_fig_{idx}.png")
    main_fig.savefig(main_png, dpi=settings['report']['quality']['dpi'])
    plt.close(main_fig)

    # ── optional donut figure ──────────────────────────────
    donut_png = None
    if settings['visualization']['subsequent_pages']['donut']:
        donut_fig, _ = make_donut_fig(sleep_period, sub_wear_idx)
        donut_png = os.path.join(tmp_dir, f"donut_fig_{idx}.png")
        donut_fig.savefig(donut_png, dpi=settings['report']['quality']['dpi'])
        plt.close(donut_fig)

    stats = get_sleep_statistics(sleep_period, sub_wear_idx)
    return idx, main_png, donut_png, sleep_period, stats


def generate_pages_parallel(
    recording: SleepRecording,
    tmp_dir: str,
    wear_idx: pd.Series,
    settings: dict,
) -> FPDF:
    """
    Build a multi-page PDF report.

    Workflow
    --------
    1.  Render the main page in the parent process.
    2.  Create a job tuple for every sleep period (`wear_blocks`).
    3.  Use `ProcessPoolExecutor` to render each sub-page's figures in
        parallel; each worker returns `(idx, main_png, donut_png,
        SleepRecording, stats)`.
    4.  Collect all results, **sort by `idx` to keep chronological order**, then
        assemble pages sequentially in the parent process
        (`pdf.add_page()`, `pdf.image()`, `pdf.text()`…).

    Parameters
    ----------
    recording     : SleepRecording
        Labeled recording (already analysed by the classifier).
    tmp_dir       : str
        Temporary directory; workers write their PNGs here.
    wear_idx      : pd.Series[bool]
        Boolean series (same index as `recording`) marking wear time.
    settings      : dict
        Complete settings tree read from *settings.json*.

    Returns
    -------
    FPDF
        Finished `FPDF` instance; caller is responsible for `pdf.output()`.
    """
    print("Status: Compiling PDF main page...")
    sns.set_theme()
    
    sleep_statistics = get_sleep_statistics(recording, wear_idx)
    pdf = FPDF(orientation="P", unit="mm", format="A4")

    # MAIN PAGE
    main_fig, _ = make_main_fig(recording, wear_idx, settings, isMainPage=True)
    main_png = os.path.join(tmp_dir, "main_fig.png")
    main_fig.savefig(main_png, dpi=settings['report']['quality']['dpi'])
    plt.close(main_fig)

    pdf.add_page()
    pdf.image("templates/nappa_report_template.png", x=0, y=0, w=210, h=297)
    pdf.image(main_png, x=6, y=35, w=200, h=133.333)
    if not settings['report']['output_formats']['figures']:
        os.remove(main_png)

    pdf.set_font("helvetica", "", 10)
    pdf.text(
        20, 10,
        f"NAPPA Summary{' '*30}"
        f"{str(recording.start)[:16]} - {str(recording.end)[:16]}{' '*30}"
        f"{recording.serial_number or 'Unknown Serial'}"
    )
    if settings['visualization']['main_page']['sleep_statistics']:
        pdf.text(25, 264, f'Recording time: {str(sleep_statistics["total_time"])[:-3]}')
        pdf.text(25, 269, f'Total sleep time: {str(sleep_statistics["total_sleep"])[:-3]}')
        pdf.text(25, 274, f'Nonwear time: {str(sleep_statistics["nonwear_time"])[:-3]}')

    if isinstance(sleep_statistics["total_time"], timedelta) and sleep_statistics["total_time"].days >= 1:
        dist_png = os.path.join(tmp_dir, "dist_fig.png")
        if settings['visualization']['main_page']['summaryfig'] == 'bar':
            make_bar_fig(recording, wear_idx, settings)
        else:
            make_violin_fig(recording, wear_idx, settings)
        plt.savefig(dist_png, dpi=settings['report']['quality']['dpi'])
        plt.close()
        pdf.image(dist_png, x=13, y=165, w=185, h=95)
        if not settings['report']['output_formats']['figures']:
            os.remove(dist_png)

    # SUB-PAGES (parallel)
    if not settings['report']['layout']['multipage']:
        return pdf

    wear_blocks = (detect_wear_blocks(wear_idx)
                   if settings['report']['layout']['auto_page_generation']
                   else settings['data']['sleep_periods'])

    jobs = [
        (i, blk, recording, wear_idx, settings, tmp_dir)
        for i, blk in enumerate(wear_blocks)
    ]

    with ProcessPoolExecutor() as pool:
        futures = {pool.submit(_render_subpage, j): j[0] for j in jobs}

        results = sorted(
                (fut.result() for fut in as_completed(futures)),
                key=lambda t: t[0]
            )

        for idx1, (idx0, main_png, donut_png, sp_rec, sp_stats) in enumerate(results, 1):

            print(f"Status: Adding PDF page {idx1}/{len(wear_blocks)}")
            # ---------- assemble one page (fast) ----------------------------
            pdf.add_page()
            pdf.image("templates/nappa_report_template.png", x=0, y=0, w=210, h=297)
            pdf.image(main_png, x=6, y=35, w=195, h=130)
            if donut_png:
                pdf.image(donut_png, x=12, y=165, w=100, h=100)

            pdf.text(20, 10, f"Sleep period {idx1}/{len(wear_blocks)}")
            pdf.text(80, 10, f"{str(sp_rec.start)[:16]} - {str(sp_rec.end)[:16]}")

            if settings['visualization']['subsequent_pages']['sleep_statistics']:
                total_time = timedelta(seconds=sp_stats["total_time"].seconds)
                total_sleep = timedelta(seconds=sp_stats["total_sleep"].seconds)
                nonwear_time = timedelta(seconds=sp_stats["nonwear_time"].seconds)
           
                pdf.text(110, 175, f'Recording time: {str(total_time)[:-3]}')
                pdf.text(110, 180, f'Total sleep time: {str(total_sleep)[:-3]}')
                pdf.text(110, 185, f'Nonwear time: {str(nonwear_time)[:-3]}')

            # cleanup
            if not settings['report']['output_formats']['figures']:
                os.remove(main_png)
                if donut_png:
                    os.remove(donut_png)

    return pdf