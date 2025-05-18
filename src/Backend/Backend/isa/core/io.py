import json
import os
import glob
import pandas as pd
import re

from nappa.objects import SleepRecording
from nappa.pipeline import read_and_process_features

def load_settings(settings_path):
    """
    Read *settings.json* from disk.

    Parameters
    ----------
    settings_path : str
        Absolute or relative path to the JSON settings file.

    Returns
    -------
    dict
        Parsed JSON as a Python dictionary.
    """
    with open(settings_path, 'r') as file:
        settings = json.load(file)
    return settings

def load_data(data_folder, time_offset):
    """
    Construct a :class:`~nappa.objects.SleepRecording` from one pair of
    *AccFeatures.csv* and *GyroFeatures.csv* files.

    The helper verifies directory layout, file count and minimum length,
    extracts the optional serial number (``SN1234``) from the file name,
    applies the user-supplied *time_offset*, and returns a fully populated
    ``SleepRecording``.

    Parameters
    ----------
    data_folder : str
        Path to a directory that contains **exactly one** pair of
        ``*AccFeatures*.csv`` and ``*GyroFeatures*.csv``.
        A nested single sub-folder is also accepted.
    time_offset : int
        UTC offset in hours; passed through to
        :func:`nappa.pipeline.read_and_process_features`.

    Returns
    -------
    SleepRecording
        The processed feature DataFrame wrapped in a recording object.

    Raises
    ------
    FileNotFoundError
        If the expected files are missing or empty.
    FileExistsError
        If more than one Acc/Gyro features file is found.
    ValueError
        If either CSV contains less than one hour of 30-s epochs.

    Notes
    -----
    *AccFeatures* / *GyroFeatures* must each contain ≥ 120 rows
    (30 s x 120 = 1 h) for downstream analysis to work.
    """
    serialNumber = None
    subdirs = [x[0] for x in os.walk(data_folder)]
    if len(subdirs) == 2:
        acc_files = glob.glob(subdirs[-1] + "/*AccFeatures*.csv")
        gyro_files = glob.glob(subdirs[-1] + "/*GyroFeatures*.csv")
    elif len(subdirs) == 1:
        acc_files = glob.glob(data_folder + "/*AccFeatures*.csv")
        gyro_files = glob.glob(data_folder + "/*GyroFeatures*.csv")
    else:
        raise FileNotFoundError("Directory structure is not supported. Please provide a zip archive with single folder containing only one set of Acc & Gyro features.")

    if len(acc_files) == 0:
        raise FileNotFoundError("No Acc features found in the specified folder. Make sure that the Acc features file is present and contains 'AccFeatures.csv' in its name.")
    if len(gyro_files) == 0:
        raise FileNotFoundError("No Gyro features found in the specified folder. Make sure that the Gyro feature file is present and contains 'GyroFeatures.csv' in its name.")
    if len(acc_files) > 1:
        raise FileExistsError("Multiple Acc features found in the specified folder. Please provide a folder with only one Acc and Gyro feature file.")
    if len(gyro_files) > 1:
        raise FileExistsError("Multiple Gyro features found in the specified folder. Please provide a folder with only one Acc and Gyro feature file.")

    acc_file = acc_files[0]
    gyro_file = gyro_files[0]

    # Look for SN (=Serial number) in the filename (from old recordings).
    # NOTE: delete this later..
    if 'SN' in acc_file:
        match = re.search(r'SN\d+', acc_file)
        if match:
            serialNumber = match.group()
    else:
        serialNumber = os.path.basename(acc_file).split('_')[0][:-1]
        if 'AccFeatures' in serialNumber:
            serialNumber = None

    acc_df = pd.read_csv(acc_file, low_memory=False)
    gyro_df = pd.read_csv(gyro_file, low_memory=False)
    if len(acc_df) == 0:
        raise FileNotFoundError("Acc features file is empty. Please provide a valid Acc features file.")
    if len(gyro_df) == 0:
        raise FileNotFoundError("Gyro features file is empty. Please provide a valid Gyro features file.")
    if len(acc_df) < 120:
        raise ValueError("Acc features file contains less than an hour of data.")
    if len(gyro_df) < 120:
        raise ValueError("Gyro features file contains less than an hour of data.")

    feature_df = read_and_process_features(acc_path=acc_file, gyro_path=gyro_file, time_offset=time_offset)   

    return SleepRecording(feature_df, serial_number=serialNumber)

