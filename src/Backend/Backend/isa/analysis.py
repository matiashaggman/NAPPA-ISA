import torch
import numpy as np
import pandas as pd
import os
import glob
import zipfile
import copy

from isa.core.plots     import init_plot_style
from isa.core.report    import generate_pages_parallel

from nappa.preprocess   import StandardScaler
from nappa.objects      import SleepRecording
from nappa.pipeline     import select_default_features
from nappa.models       import NappaSleepNet
from nappa.plots        import SleepDepthTrend

FEATURE_MEANS = np.array([0.28299643,  0.40674336, 27.51102132,  1.25385624,  1.54872324])
FEATURE_STDS  = np.array([1.08733522,  0.34976171, 46.77687801,  3.8659115,   9.01733374])


def nappa_analysis(recording:SleepRecording, wear_idx:pd.Series, output_file:str,
                    tempfolder:str, settings:dict):
    """
    End-to-end NAPPA analysis pipeline.

    Steps performed
    ---------------
    1.  Initialise Matplotlib / Seaborn style (`init_plot_style`).
    2.  Configure a `NappaSleepNet` classifier
        - full feature set or accelerometer-only depending on
          `settings['report']['classifier_input']['accelerometer_only']`.
    3.  Slice the `recording` to *start..end* defined in `settings['data']`;
        apply global z-score scaling to the features.
    4.  Run the classifier and obtain sleep-stage probabilities.
    5.  Compute sleep-depth trend **and 95 % CI** via
        `SleepDepthTrend`, then attach all labels to a new
        `SleepRecording` instance (`analyzedRecording`).
    6.  Generate the PDF report (main page + sub-pages).  
        Sub-pages are rendered **in parallel** by
        `core.report.generate_pages_parallel()`.
    7.  Depending on `settings['report']['output_formats']`, write:
        * /<temp>/NAPPA_REPORT_*.pdf  
        * /<temp>/output.csv (feature + label table)  
        * zero or more PNG figures
    8.  Pack selected outputs into *output_file* (ZIP).
    9.  Emit human-readable progress through *status_callback* if supplied.

    Parameters
    ----------
    recording : SleepRecording
        Raw features for the whole recording.
    wear_idx  : pd.Series[bool]
        Boolean mask (same datetime index as *recording*) indicating
        periods when the wearable was worn.
    output_file : str
        Path for the final **ZIP** archive.
    tempfolder  : str
        Temporary working directory - large intermediate files are
        created here and cleaned up by the caller.
    settings : dict
        Parsed contents of *settings.json* sent by the GUI.
    status_callback : callable(str), optional
        Callback invoked with status messages (e.g. for a GUI progress bar).

    Returns
    -------
    None
        Results are written to *output_file* as a ZIP archive.

    Raises
    ------
    RuntimeError
        If classifier weights are missing or PDF generation fails.
    """

    init_plot_style()

    start = settings['data']['start_time']
    end = settings['data']['end_time']

    if len(start) == 0 or len(end) == 0:
        #raise ValueError("Start and end times must be strings in the format 'YYYY-MM-DD HH:MM:SS'.")
        start = recording.start
        end = recording.end

    features = recording.features[start:end]
    wear_idx = wear_idx[start:end] #type:ignore

    scaler = StandardScaler(method='global')

    print("Status: setting up classifier...")

    model = None
    if not settings['report']['classifier_input']['accelerometer_only']:
        model = NappaSleepNet().load('weights/weights_full.pth')
        x = select_default_features(copy.deepcopy(features)).to_numpy()
        x = scaler(data=x, with_mean=FEATURE_MEANS, with_std=FEATURE_STDS)
    else:
        model = NappaSleepNet(num_features=1).load('weights/weights_acc.pth')
        x = features.loc[:, 'activity'].to_numpy().reshape(-1, 1)
        x = scaler(data=x, with_mean=FEATURE_MEANS[0], with_std=FEATURE_STDS[0])

    x = torch.tensor(x, dtype=torch.float)

    print("Status: running classifier...")

    y = model.predict(x).numpy()
    [sdt, lowerlim, upperlim] = SleepDepthTrend(y[:, 1:])

    labels = pd.DataFrame(y, columns=['sleep_stage', 'p(deep)', 'p(light)', 'p(wake)'], index=features.index)
    labels['sleep_stage'] = labels['sleep_stage'].replace({0:'deep', 1:'light', 2:'wake'})
    labels['sdt'] = pd.Series(sdt, index=features.index)
    labels['sdt_ci_lower'] = pd.Series(lowerlim, index=features.index)
    labels['sdt_ci_upper'] = pd.Series(upperlim, index=features.index)

    analyzedRecording = SleepRecording(features, labels, serial_number=recording.serial_number)

    zf = zipfile.ZipFile(output_file, mode="w")
    
    if settings['report']['output_formats']['pdf']:
        pdf = generate_pages_parallel(
                recording=analyzedRecording,
                settings=settings,
                wear_idx=wear_idx,
                tmp_dir=tempfolder
            )

        print("Status: writing .pdf output file...")

        sn = analyzedRecording.serial_number if analyzedRecording.serial_number else ""
        if sn == "":
            fname = "NAPPA_REPORT_" + str(analyzedRecording.start.date()) + ".pdf" #type:ignore
        else:
            fname = "NAPPA_REPORT_" + sn + "_" + str(analyzedRecording.start.date()) + ".pdf" #type:ignore
        output = os.path.join(tempfolder, fname) 

        pdf.output(output)
        zf.write(output, os.path.basename(output))    
    
    if settings['report']['output_formats']['csv']:
        print("Status: writing .csv output file...")
    
        output = os.path.join(tempfolder, 'output.csv')
        analyzedRecording.save(output)
        zf.write(output, os.path.basename(output))

    if settings['report']['output_formats']['figures']:
        print("Status: saving figures as PNG files...")
    
        for png_file in glob.glob(os.path.join(tempfolder, '*.png')):
            zf.write(png_file, os.path.basename(png_file))
    zf.close()

    print("Status: analysis complete.")
    return