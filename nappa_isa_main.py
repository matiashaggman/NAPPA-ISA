# Copyright Baba Center

import glob
import os
import sys
import re
import copy
import zipfile
import logging
import json
import tempfile

from datetime import timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import torch

import seaborn as sns
import numpy as np
import pandas as pd


from fpdf import FPDF
from scipy.signal import medfilt, spectrogram

from nappa.objects import SleepRecording
from nappa.preprocess import StandardScaler
from nappa.pipeline import read_and_process_features, select_default_features
from nappa.plots import caltrendwithCI

from nappa.models import NappaSleepNet

color_palette = sns.color_palette('Set2')
coolwarm_palette = sns.color_palette(palette='coolwarm')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tempfolder = tempfile.gettempdir() + '\\NAPPA-ISA'

FEATURE_MEANS = np.array([0.28299643,  0.40674336, 27.51102132,  1.25385624,  1.54872324])
FEATURE_STDS  = np.array([1.08733522,  0.34976171, 46.77687801,  3.8659115,   9.01733374])


def init_plot_style():
    """
    Initialize the global plot style once at the start of the script.
    """
    sns.set_theme()  # Or any other style you want
    plt.rcParams.update({
        'font.size': 14,
        'axes.titlesize': 16,
        'axes.labelsize': 14,
        'xtick.labelsize': 12,
        'ytick.labelsize': 12,
        'legend.fontsize': 12,
        'figure.autolayout': True
    })
    return 


def plot_segments(ax, x, mask, color, y=None, step=False, CI=None):
    """
    Plot segments of data on the given axes.

    Parameters:
    ax : matplotlib.axes.Axes
        The axes to plot on.
    x : array-like
        The x data.
    y : array-like
        The y data.
    mask : array-like of bool
        A boolean mask indicating which segments to plot.
    color : str
        The color to use for the plotted segments.
    step : bool
        Use step function over plot for discrete data.
    """
    # Convert bool to int to find transitions
    mask_int = mask.astype(int)
    transitions = np.diff(mask_int)
    start_pts = np.where(transitions == 1)[0] + 1
    end_pts = np.where(transitions == -1)[0] + 1

    # If the mask starts True at index 0
    if mask_int.iloc[0] == 1:
        start_pts = np.insert(start_pts, 0, 0)
    # If the mask ends True at last index
    if mask_int.iloc[-1] == 1:
        end_pts = np.append(end_pts, len(mask_int))

    if CI is None:
        if not step:
            for s, e in zip(start_pts, end_pts):
                ax.plot(x[s:e], y[s:e], color=color, linewidth=1)
        else:
            for s, e in zip(start_pts, end_pts):
                ax.step(x[s:e], y[s:e], color=color, linewidth=1)

    else:
        for s, e in zip(start_pts, end_pts):
            ax.fill_between(x[s:e], CI[0][s:e], CI[1][s:e], color=color, alpha=0.3)

    return


def make_donut_fig(recording, wear_idx):
    """
    Create a donut plot for sleep stage distribution.

    Parameters:
    recording : SleepRecording
        The sleep recording object containing labels.
    wear_idx : array-like of bool
        A boolean mask indicating the wear time indexes.

    Returns:
    fig : matplotlib.figure.Figure
        The created figure.
    ax : matplotlib.axes.Axes
        The axes of the created figure.
    """
    sleep_df = recording.labels[wear_idx]

    stage_counts = sleep_df['sleep_stage'].value_counts()
    stage_proportions = stage_counts / stage_counts.sum()

    sns.set_theme()
    fig, ax = plt.subplots(figsize=(6, 6))

    # Create the donut plot
    colors = sns.color_palette(palette='coolwarm')
    color_mapping = {'deep': colors[0], 'light': colors[1], 'wake': colors[2]}
    stage_colors = [color_mapping[stage] for stage in stage_proportions.index]

    wedges, texts, autotexts = ax.pie(
        stage_proportions,
        labels=stage_proportions.index,
        autopct='%1.0f%%',
        startangle=90,
        colors=stage_colors,
        wedgeprops={'width': 0.3},
        textprops={'color': 'black', 'fontsize': 12}
    )

    center_circle = plt.Circle((0, 0), 0.5, color='white', zorder=10)
    ax.add_artist(center_circle)

    ax.set_title("Sleep Stage Distribution")

    return fig, ax


def make_bar_fig(recording, wear_idx, options):
    """
    Generates a bar plot figure showing the distribution of sleep stages over time.
    Parameters:
    recording (object): The recording object containing sleep stage data.
    wear_idx (int): The index of the wearable device data to be used.
    options (dict): A dictionary containing options for the plot. 
                    Expected key is 'date_style' with values:
                    0 - '%d.%m.'
                    1 - '%d/%m'
                    2 - '%d.%m.%y'
                    3 - '%d/%m/%y'
    Returns:
    matplotlib.axes._subplots.AxesSubplot: The Axes object with the bar plot.
    """

    match options['date_style']:
        case 0:
            dateFmt = '%d.%m.'
        case 1:
            dateFmt = '%d/%m'
        case 2:
            dateFmt = '%d.%m.%y'
        case 3:
            dateFmt = '%d/%m/%y'
        case _:
           dateFmt =  '%d.%m.'

    df = recording.labels[wear_idx]

    dates_df = pd.to_datetime(pd.Series(df.index.date, name='date')).dt.strftime(dateFmt)
    dates_df.index = df.index

    df = pd.concat([df, dates_df], axis=1)
    df = df.drop(columns=['p(deep)', 'p(light)', 'p(wake)'])

    df_counts = df.groupby(['date', 'sleep_stage']).size().unstack(fill_value=0)

    sns.set_theme()
    ax = df_counts.plot(kind='bar', stacked=True, figsize=(10, 4), color=coolwarm_palette)

    ax.set_title('Sleep stages distribution over time')
    plt.xticks(rotation=0)

    y_labels = ax.get_yticks()
    ax.set_yticklabels([f"{int(y*30/(60*60))}" for y in y_labels])
    ax.set_ylabel('Hours')

    plt.legend(title='Sleep stages', bbox_to_anchor=(0.7, -0.1), ncols=3, frameon=False)

    plt.xlabel('')
    plt.tight_layout()

    return ax


def make_violin_fig(recording, wear_idx, options):
    """
    Generates a violin plot figure to visualize sleep stage distribution over time.
    Parameters:
    recording (object): The recording object containing sleep data.
    wear_idx (int): The index of the wear period to be analyzed.
    options (dict): A dictionary containing options for the plot. 
                    Expected key is 'date_style' with possible values:
                    0 - '%d.%m.'
                    1 - '%d/%m'
                    2 - '%d.%m.%y'
                    3 - '%d/%m/%y'
    Returns:
    matplotlib.axes._subplots.AxesSubplot: The Axes object with the violin plot.
    """

    match options['date_style']:
        case 0:
            dateFmt = '%d.%m.'
        case 1:
            dateFmt = '%d/%m'
        case 2:
            dateFmt = '%d.%m.%y'
        case 3:
            dateFmt = '%d/%m/%y'
        case _:
           dateFmt =  '%d.%m.'

    df = recording.labels[wear_idx]

    dates_df = pd.to_datetime(pd.Series(df.index.date, name='date')).dt.strftime(dateFmt)
    dates_df.index = df.index

    df = pd.concat([df, dates_df], axis=1)

    fig, ax = plt.subplots(figsize=(10, 4))

    sns.violinplot(
        data=df, x='date',
        y='sdt', inner=None,
        ax=ax, zorder=2,
        color=coolwarm_palette[0]
    )

    ax.axhline(y=1.5, color='black', linestyle='--', zorder=3, alpha=1, linewidth=1)
    ax.axhline(y=2.5, color='black', linestyle='--', zorder=3, alpha=1, linewidth=1)

    ax.set_title('Sleep Stage Distribution Over Time')
    plt.yticks([1,2,3], ['Deep', 'Light', 'Wake'])
    plt.xlabel('')
    plt.ylabel('')
    plt.tight_layout()

    return ax


def make_main_fig(recording, wear_idx, options, main_page):
    """    
    Creates a multi-panel figure showing sleep depth, activity, and posture.
    Parameters:
    recording : SleepRecording object
    wear_idx : array-like
        Boolean array indicating whether the sensor was worn at each time point.
    options : dict
    Returns:
    fig : matplotlib.figure.Figure
        The created figure.
    axes : array of matplotlib.axes._subplots.AxesSubplot
        The axes of the subplots in the figure.
    """

    time = recording.timestamps
    features = recording.features
    sdt = recording.labels.loc[:, 'sdt']
    sdt_lower = recording.labels.loc[:, 'sdt_ci_lower']
    sdt_upper = recording.labels.loc[:, 'sdt_ci_upper']

    hypnogram = recording.labels.loc[:, 'sleep_stage'].replace({'wake':2, 'light':1, 'deep':0}).infer_objects(copy=False)

    if options['median_filter']:
        sdt = medfilt(sdt, kernel_size=options['filter_window'])
        sdt_lower = medfilt(sdt_lower, kernel_size=options['filter_window'])
        sdt_upper = medfilt(sdt_upper, kernel_size=options['filter_window'])

    sdt_plot = False # If sdt_plot = false, then we print a discrete hypnogram.
    sdt_ci = False
    activity_plot = False
    respiration_rate_plot = False
    position_plot = False
    if main_page:
        sdt_plot = options['plots']['sdt']
        sdt_ci = options['plots']['sdt_ci']
        activity_plot = options['plots']['activity']
        respiration_rate_plot = options['plots']['respiration_rate']
        position_plot = options['plots']['position']
    else:
        sdt_plot = options['plots']['subsequent_sdt']
        sdt_ci = options['plots']['subsequent_sdt_ci']
        activity_plot = options['plots']['subsequent_activity']
        respiration_rate_plot = options['plots']['subsequent_respiration_rate']
        position_plot = options['plots']['subsequent_position']


    height_ratios = [4, 2 if activity_plot else 0, 2 if respiration_rate_plot else 0, 1 if position_plot else 0]
    height_ratios = [ratio for ratio in height_ratios if ratio > 0]

    if len(height_ratios) == 0:
        raise ValueError("No plots selected. Please select at least one plot to display.")

    fig, axes = plt.subplots(
        figsize=(12, 8),
        nrows=len(height_ratios),
        ncols=1, sharex=True,
        gridspec_kw={"height_ratios": height_ratios}
    )

    if len(height_ratios) == 1:
        axes = [axes]

    plot_idx = 0

    # PLOT #1: Sleep Depth or discrete hypnogram
    if sdt_plot:  # Plot SDT
        if options['filter_nonwear']:
            plot_segments(ax=axes[plot_idx], x=time, y=sdt, mask=wear_idx, color=coolwarm_palette[0])
            plot_segments(ax=axes[plot_idx], x=time, y=sdt, mask=~wear_idx, color=color_palette[-1])
            if sdt_ci:
                plot_segments(ax=axes[plot_idx], x=time, CI=(sdt_lower, sdt_upper), mask=wear_idx, color=coolwarm_palette[-1])
                plot_segments(ax=axes[plot_idx], x=time, CI=(sdt_lower, sdt_upper), mask=~wear_idx, color=color_palette[-1])
        else:
            axes[plot_idx].plot(time, sdt, color=coolwarm_palette[0])
            if sdt_ci:
                axes[plot_idx].fill_between(time, sdt_lower, sdt_upper, color=coolwarm_palette[-1], alpha=0.3)

        axes[plot_idx].axhline(y=1.5, color='black', linestyle='--', zorder=1, alpha=1, linewidth=1)
        axes[plot_idx].axhline(y=2.5, color='black', linestyle='--', zorder=1, alpha=1, linewidth=1)
        axes[plot_idx].set_ylim(0.5, 3.5)
        axes[plot_idx].set_yticks([1, 2, 3])
    else:  # Plot a discrete hypnogram instead
        if options['filter_nonwear']:
            plot_segments(ax=axes[plot_idx], x=time, y=hypnogram, mask=wear_idx, color=coolwarm_palette[0])
            plot_segments(ax=axes[plot_idx], x=time, y=hypnogram, mask=~wear_idx, color=color_palette[-1])
        else:
            axes[plot_idx].step(time, hypnogram, color=coolwarm_palette[0])
        axes[plot_idx].set_yticks([0, 1, 2])

    axes[plot_idx].set_yticklabels(["Deep", "Light", "Wake"])
    axes[plot_idx].set_title("Sleep depth")
    plot_idx += 1

    # PLOT #2: Activity
    if activity_plot:
        if options['median_filter']:
            activity_feature = medfilt(features.loc[:, 'activity'], kernel_size=options['filter_window'])
        else:
            activity_feature = features.loc[:, 'activity']

        if options['log_scale']:
            activity_feature = np.log10(np.abs(activity_feature))

        if options['filter_nonwear']:
            plot_segments(ax=axes[plot_idx], x=time, y=activity_feature, mask=wear_idx, color=coolwarm_palette[0])
            plot_segments(ax=axes[plot_idx], x=time, y=activity_feature, mask=~wear_idx, color=color_palette[-1])
        else:
            axes[plot_idx].plot(time, activity_feature, color=coolwarm_palette[0])

        axes[plot_idx].set_yticks([])
        axes[plot_idx].set_ylabel("Activity", rotation=0, labelpad=25)
        plot_idx += 1

    # PLOT #3: Respiration rate
    if activity_plot:
        if options['median_filter']:
            respiration_rate_feature = medfilt(features.loc[:, 'resp_rate_y'], kernel_size=options['filter_window'])
        else:
            respiration_rate_feature = features.loc[:, 'resp_rate_y']

        if options['filter_nonwear']:
            plot_segments(ax=axes[plot_idx], x=time, y=respiration_rate_feature, mask=wear_idx, color=coolwarm_palette[0])
            plot_segments(ax=axes[plot_idx], x=time, y=respiration_rate_feature, mask=~wear_idx, color=color_palette[-1])
        else:
            axes[plot_idx].plot(time, respiration_rate_feature, color=coolwarm_palette[0])

        axes[plot_idx].set_yticks([])
        axes[plot_idx].set_ylabel("Respiration\nrate", rotation=0, labelpad=35)
        plot_idx += 1  

    # PLOT #4: Body Position
    if position_plot:
        pos = features.loc[:, 'body_pos']
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 1), color=color_palette[0],
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Prone')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 2), color=color_palette[3],
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Supine')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 3), color=color_palette[2],
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Right side')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 4), color="#a1c9f4",
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Left side')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 5), color="#d0bbff",
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Head down')
        axes[plot_idx].fill_between(time, 0, 1, where=(pos == 6), color=color_palette[6],
                                    transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Head up')

        if options['filter_nonwear']:
            axes[plot_idx].fill_between(time, 0, 1, where=~wear_idx, color=color_palette[-1],
                                        transform=axes[plot_idx].get_xaxis_transform(), interpolate=True, label='Sensor not worn')

        axes[plot_idx].legend(loc='upper center', bbox_to_anchor=(0.5, -0.5), ncol=4, frameon=False)
        axes[plot_idx].set_yticks([])
        axes[plot_idx].set_ylabel("Posture", rotation=0, labelpad=25)

    # X-axis formatting
    match options['date_style']:
        case 0:
            date_fmt = mdates.DateFormatter('%d.%m. %H')
        case 1:
            date_fmt = mdates.DateFormatter('%d/%m %H')
        case 2:
            date_fmt = mdates.DateFormatter('%d.%m.%y %H')
        case 3:
            date_fmt = mdates.DateFormatter('%d/%m/%y %H')
        case 4:
            date_fmt = mdates.DateFormatter('%H:%M')
        case _:
            date_fmt = mdates.DateFormatter('%H:%M')

    if recording.duration <= pd.Timedelta(days=1):
        # If total duration is less than a day, show hours+minutes
        date_fmt = mdates.DateFormatter('%H:%M')
        locator = mdates.AutoDateLocator(minticks=12, maxticks=12)
    else:
        locator = mdates.AutoDateLocator(minticks=options['x_ticks'], maxticks=options['x_ticks'])

    axes[-1].xaxis.set_major_locator(locator)
    axes[-1].xaxis.set_major_formatter(date_fmt)

    #plt.tight_layout()
    return fig, axes


def get_sleep_statistics(recording, wear_idx):
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


def detect_wear(feature, threshold=0.009, seg_len=120, overlap=119, min_nonwear_duration=1800):
    """
    Detects wear time periods from a given feature vector (designed for activity).
    Parameters:
    feature : pandas.Series
        The feature vector to analyze.
    threshold : float
        The threshold value for detecting wear periods.
    seg_len : int
        The length of the segments for the spectrogram.
    overlap : int
        The overlap between segments for the spectrogram.
    min_nonwear_duration : int
        The minimum duration of non-wear time to be considered as non-wear.
    Returns:
    wear : pandas.Series
        A boolean series indicating wear periods.
    """
    f, t, Sxx = spectrogram(
        feature.to_numpy(),
        fs=1/30,
        nperseg=seg_len,
        noverlap=overlap,
    )
    # Heuristic for wear detection. Might need improvements in the future
    threshold_fn = (10 * np.log10(np.max(Sxx, axis=0) + 1e-10) / 1e4) + 0.01

    wear_idx = threshold_fn > threshold

    time_index = [feature.index[0] + pd.Timedelta(seconds=int(x)) for x in t]

    wear_df = pd.DataFrame(wear_idx, index=time_index, columns=['wear'])

    aligned_wear = wear_df.reindex(feature.index, method='nearest')

    aligned_wear = aligned_wear.resample('30s').mean().ffill().astype(bool)

    # Remove false negatives by thresholding the number of consecutive nonwear time points
    nonwear_blocks = (aligned_wear['wear'] == False).astype(int).groupby(aligned_wear['wear'].ne(aligned_wear['wear'].shift()).cumsum()).cumsum()
    aligned_wear.loc[nonwear_blocks < (min_nonwear_duration / 30), 'wear'] = True

    return aligned_wear['wear'] # return pandas series instead of df for simplicity.


def detect_wear_blocks(wear_idx, threshold_length=pd.Timedelta(hours=4), buffer_length=pd.Timedelta(minutes=30)):
    wearTime = wear_idx  # wear_idx is a Series of booleans indexed by time
    wearBlocks = []
    current_block = []

    # Iterate over the Series
    for index, row in wearTime.items():
        if row:
            current_block.append(index)
        else:
            if current_block:
                if (current_block[-1] - current_block[0]) >= threshold_length:
                    wearBlocks.append((
                        current_block[0] - buffer_length,
                        current_block[-1] + buffer_length,
                    ))
                current_block = []

    if current_block:
        if (current_block[-1] - current_block[0]) >= threshold_length:
            wearBlocks.append((
                current_block[0] - buffer_length,
                current_block[-1] + buffer_length,
            ))

    wearBlocks = [(start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")) for start, end in wearBlocks]
    
    return wearBlocks


def load_data(data_folder, time_offset):

    serialNumber = None
    subdirs = [x[0] for x in os.walk(data_folder)]
    if len(subdirs) == 2:
        acc_file = glob.glob(subdirs[-1] + "/*AccFeatures*.csv")[0]
        gyro_file = glob.glob(subdirs[-1] + "/*GyroFeatures*.csv")[0]
    elif len(subdirs) == 1:
        acc_file = glob.glob(data_folder + "/*AccFeatures*.csv")[0]
        gyro_file = glob.glob(data_folder + "/*GyroFeatures*.csv")[0]
    else:
        return

    if 'SN' in acc_file:
        match = re.search(r'SN\d+', acc_file)
        if match:
            serialNumber = match.group()

    feature_df = read_and_process_features(acc_path=acc_file, gyro_path=gyro_file, time_offset=time_offset)   

    return SleepRecording(feature_df, serial_number=serialNumber)


def generate_pages(recording, tmp_dir, wear_idx, options, status_callback=None):
    """
    Generates a multi-page PDF report summarizing sleep statistics and visualizations.
    Parameters:
    recording (SleepRecording): The already analyzed sleep recording data (containing labels).
    tmp_dir (str): Temporary directory for storing intermediate files.
    wear_idx (pd.DataFrame): DataFrame indicating wear times.
    options (dict): Dictionary of options for generating the report, including plot types and DPI settings.
    status_callback (callable, optional): Function to call with status updates.
    Returns:
    FPDF: The generated PDF report.
    """
    
    msg = "Status: Compiling PDF main page..."
    if status_callback:
        status_callback(msg)
    logger.info(msg)

    sleep_statistics = get_sleep_statistics(recording, wear_idx)
    pdf = FPDF(orientation="P", unit="mm", format="A4")

    # MAIN PAGE
    pdf.add_page()
    main_fig, main_axes = make_main_fig(recording, wear_idx, options, main_page=True)
    main_fig_path = os.path.join(tmp_dir, "temp_main_fig.png")
    main_fig.savefig(main_fig_path, dpi=options['report_dpi'])
    plt.close(main_fig)

    # Template background
    pdf.image("templates/nappa_report_template.png", x=0, y=0, w=210, h=297)
    pdf.image(main_fig_path, x=6, y=35, w=195, h=130)
    os.remove(main_fig_path)

    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    
    pdf.text(20, 10,f'NAPPA Summary{" "*30}{str(recording.start)[0:16]}  -  {str(recording.end)[0:16]}{" "*30}{recording.serial_number if recording.serial_number else "Unknown Serial"}')

    pdf.text(25, 254, f'Recording time: {str(sleep_statistics["total_time"])[:-3]}')
    pdf.text(25, 259, f'Total sleep time: {str(sleep_statistics["total_sleep"])[:-3]}')
    pdf.text(25, 264, f'Nonwear time: {str(sleep_statistics["nonwear_time"])[:-3]}')

    # If more than 1 day, add a bar/violin summary
    if sleep_statistics["total_time"].days >= 1:
        dist_fig_path = os.path.join(tmp_dir, "temp_dist_fig.png")
        if options['plots']['summary_fig'] == 'bar':
            make_bar_fig(recording, wear_idx, options)
            plt.savefig(dist_fig_path, dpi=options['report_dpi'])
            plt.close()
            pdf.image(dist_fig_path, x=15, y=165, w=185, h=78)
        elif options['plots']['summary_fig'] == 'violin':
            make_violin_fig(recording, wear_idx, options)
            plt.savefig(dist_fig_path, dpi=options['report_dpi'])
            plt.close()
            pdf.image(dist_fig_path, x=6, y=165, w=190, h=76)
        os.remove(dist_fig_path)

    # SUBSEQUENT PAGES
    if options['multipage']:
        if options['page_generation_automatic']:
            wear_blocks = detect_wear_blocks(wear_idx)
        else:
            wear_blocks = options['sleep_periods']  # Provided by user?

        for i, (period_start, period_end) in enumerate(wear_blocks):
            msg = f"Generating PDF page ({i+1}/{len(wear_blocks)})"
            logger.info(msg)
            if status_callback:
                status_callback(f"Status: {msg}")

            sleep_period = SleepRecording(
                features=recording.features.loc[period_start:period_end],
                labels=recording.labels.loc[period_start:period_end]
            )
            sub_wear_idx = wear_idx.loc[period_start:period_end]
            sp_statistics = get_sleep_statistics(sleep_period, sub_wear_idx)

            pdf.add_page()
            sub_main_fig, _ = make_main_fig(sleep_period, sub_wear_idx, options, main_page=False)
            sub_main_fig_path = os.path.join(tmp_dir, f"temp_main_fig_{i}.png")
            sub_main_fig.savefig(sub_main_fig_path, dpi=options['report_dpi'])
            plt.close(sub_main_fig)

            donut_fig, _ = make_donut_fig(sleep_period, sub_wear_idx)
            donut_fig_path = os.path.join(tmp_dir, f"temp_donut_fig_{i}.png")
            donut_fig.savefig(donut_fig_path, dpi=options['report_dpi'])
            plt.close(donut_fig)

            pdf.image("templates/nappa_report_template.png", x=0, y=0, w=210, h=297)
            pdf.image(sub_main_fig_path, x=6, y=35, w=195, h=130)
            pdf.image(donut_fig_path, x=12, y=165, w=100, h=100)

            os.remove(sub_main_fig_path)
            os.remove(donut_fig_path)

            pdf.text(20, 10, f'Sleep period {i+1}/{len(wear_blocks)}')
            pdf.text(80, 10, f'{str(sleep_period.start)[0:16]}  -  {str(sleep_period.end)[0:16]}')

            pdf.text(110, 174, f'Recording time: {str(sp_statistics["total_time"])[:-3]}')
            pdf.text(110, 179, f'Nonwear time: {str(sp_statistics["nonwear_time"])[:-3]}')
            pdf.text(110, 184, f'Total sleep time: {str(sp_statistics["total_sleep"])[:-3]}')

    return pdf


def nappa_analysis(recording, wear_idx, output_file, tempfolder, options=None, status_callback=None):
    """
    Run the NAPPA analysis pipeline on a given SleepRecording object.
    Parameters:
    recording (SleepRecording): The SleepRecording object containing the sleep data to be analyzed.
    output_file (str): The path to the output file where the results will be saved.
    tempfolder (str): The path to a temporary folder for intermediate files.
    options (dict, optional): A dictionary of options to customize the analysis.
    status_callback (function, optional): A callback function to report the status of the analysis.
    Returns:
    None
    This function performs the following steps:
    1. Initializes the plot style.
    2. Sets up the classifier based on the provided options.
    3. Loads the sleep data from the recording object.
    4. Runs the classifier to predict sleep stages.
    5. Generates labels for the sleep stages and calculates sleep depth trend
    6. Detects wear periods from the activity data.
    7. Generates a PDF report and/or CSV output based on the provided options.
    8. Writes the results to a zip file.
    9. Reports the status of the analysis through the status_callback function.
    """
    init_plot_style()

    start = options['start_time']
    end = options['end_time']

    features = recording.features[start:end]

    scaler = StandardScaler(method='global')

    msg="Status: setting up classifier..."
    if status_callback:
        status_callback(msg)
    logger.info(msg)

    model = None
    if options['full_features']:
        model = NappaSleepNet().load('weights/weights_full.pth')
        x = select_default_features(copy.deepcopy(features)).to_numpy()
        x = scaler(data=x, with_mean=FEATURE_MEANS, with_std=FEATURE_STDS)
    else:
        model = NappaSleepNet(num_features=1).load('weights/weights_acc.pth')
        x = features.loc[:, 'activity'].to_numpy().reshape(-1, 1)
        x = scaler(data=x, with_mean=FEATURE_MEANS[0], with_std=FEATURE_STDS[0])

    x = torch.tensor(x, dtype=torch.float)

    msg= "Status: running classifier..."
    if status_callback:
        status_callback(msg)
    logger.info(msg)

    y = model.predict(x).numpy()
    [sdt, lowerlim, upperlim] = caltrendwithCI(copy.deepcopy(y[:, 1:]))

    labels = pd.DataFrame(y, columns=['sleep_stage', 'p(deep)', 'p(light)', 'p(wake)'], index=features.index)
    labels['sleep_stage'] = labels['sleep_stage'].replace({0:'deep', 1:'light', 2:'wake'})
    labels['sdt'] = pd.Series(sdt, index=features.index)
    labels['sdt_ci_lower'] = pd.Series(lowerlim[:,0], index=features.index)
    labels['sdt_ci_upper'] = pd.Series(upperlim[:,0], index=features.index)

    analyzedRecording = SleepRecording(features, labels, serial_number=recording.serial_number)

    zf = zipfile.ZipFile(output_file, mode="w")
    
    if options['pdf_output']:
        pdf = generate_pages(
                recording=analyzedRecording,
                options=options,
                wear_idx=wear_idx,
                tmp_dir=tempfolder,
                status_callback=status_callback
            )

        msg="Status: writing .pdf output file..."
        if status_callback:
            status_callback(msg)
        logger.info(msg)

        rec_ID = analyzedRecording.serial_number if analyzedRecording.serial_number else "" + "_" + str(analyzedRecording.start.date())
        output = os.path.join(tempfolder, "NAPPA_") +  rec_ID + "_" + ".pdf"
        pdf.output(output)
        zf.write(output, os.path.basename(output))    
    
    if options['csv_output']:
        msg="Status: writing .pdf output file..."
        if status_callback:
            status_callback(msg)
        logger.info(msg)
    
        output = os.path.join(tempfolder, 'output.csv')
        df = pd.concat([analyzedRecording.features, analyzedRecording.labels], axis=1)
        df.to_csv(output, date_format='%Y-%m-%d %H:%M:%S')
        zf.write(output, os.path.basename(output))

    zf.close()

    msg="Status: analysis complete."
    if status_callback:
        status_callback(msg)
    logger.info(msg)

    return


def load_options(options_path):
    with open(options_path, 'r') as file:
        options = json.load(file)
    return options[0]

#Run the program
if __name__ == "__main__":
    # Default
    options = load_options('options.json')
    input_file = sys.argv[1]
    with zipfile.ZipFile(input_file, "r") as zip_ref:
        zip_ref.extractall(tempfolder)

    sleepRecording = load_data(tempfolder)
    nappa_analysis(recording=sleepRecording, output_file=input_file + "_analyzed.zip", tempfolder=tempfolder, options=options)