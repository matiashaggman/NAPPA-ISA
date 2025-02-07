import os
import json
import pandas as pd
import numpy as np

from .objects import NappaDataset, SleepRecording

def read_and_process_hypnogram(hypno_path, cfg):
    
    """
    Reads and processes a hypnogram file.
    
    Args:
        hypno_path (str): The file path to the hypnogram file.
    
    Returns:
        pd.DataFrame: A DataFrame with processed datetime and sleep stage information.
    """
        
    with open(hypno_path, 'r') as file:
        lines = file.readlines()

    # Extract start date
    start_date_str = lines[1].split('Start Time: ')[1].strip()
    start_date = pd.to_datetime(start_date_str, format='%d.%m.%Y %H:%M:%S').date()

    # Skip header
    hypnogram_df = pd.read_table(hypno_path, skiprows=8, delimiter= ' ', header=None)
    
    # If each timestamp contains also date
    if hypnogram_df.shape[1] == 3:
        hypnogram_df.columns = ['date', 'time', 'sleep_stage']
        hypnogram_df['date'] = pd.to_datetime(hypnogram_df['date'], format='%d.%m.%Y')
       
        if ',000' in str(hypnogram_df['time'][0]):
            # Standard output form from clinical hypnograms
            hypnogram_df['time'] = pd.to_datetime(hypnogram_df['time'], format='%H:%M:%S,%f;')
        else:
            # Pseudo hypnogram form
            hypnogram_df['time'] = pd.to_datetime(hypnogram_df['time'].str.strip(','), format='%H:%M:%S')


        hypnogram_df['timestamp'] = hypnogram_df['date'] + (hypnogram_df['time'] - hypnogram_df['time'].dt.normalize())
    # Else prepend date to each timestamp
    elif hypnogram_df.shape[1] == 2:

        hypnogram_df.columns = ['time', 'sleep_stage']
        hypnogram_df['time'] = pd.to_datetime(hypnogram_df['time'], format='%H:%M:%S,%f;').dt.time
        
        hypnogram_df['date'] = start_date
        hypnogram_df['timestamp'] = pd.to_datetime(hypnogram_df['date'].astype(str) + ' ' + hypnogram_df['time'].astype(str))
        
        # Look for timestamps after midnight
        rollovers = (hypnogram_df['timestamp'].diff() < pd.Timedelta(0)).cumsum()
        
        # Change the date after midnight
        hypnogram_df['timestamp'] += pd.to_timedelta(rollovers, unit='D')

    hypnogram_df = hypnogram_df[['timestamp', 'sleep_stage']]
    hypnogram_df['timestamp'] = pd.to_datetime(hypnogram_df['timestamp'])  # Convert 'datetime' column to datetime type
    hypnogram_df = hypnogram_df.set_index('timestamp')  # Set 'datetime' column as the index
    hypnogram_df = hypnogram_df[['sleep_stage']]
    # Interpolate Artifacts (A) with the previous sleep stage. TODO: Maybe Find a better way to handle hypnogram epoch artifacts (?).
    hypnogram_df['sleep_stage'] = hypnogram_df['sleep_stage'].replace('A', None).ffill()

    # Resample hypnogram to wanted time resolution.
    hypnogram_df = hypnogram_df.resample(cfg['time_resolution']).ffill().bfill()

    return hypnogram_df


def align_features_with_labels(sensor_df, hypnogram_df, cfg):
    """
    Aligns features with labels based on timestamps.
    
    Args:
        sensor_df (pd.DataFrame): DataFrame with sensor features.
        hypnogram_df (pd.DataFrame): DataFrame with a processed hypnogram.
    
    Returns:
        Tuple: Temporally aligned features and hypnogram DataFrames.
    """
    # Align indices by finding the intersection of timestamps
    common_index = sensor_df.index.intersection(hypnogram_df.index)
    
    # Filter dataframes to the common indices
    aligned_sensor_df = sensor_df.loc[common_index]
    aligned_hypnogram_df = hypnogram_df[hypnogram_df.index.isin(common_index)]
    
    # Ensure the length of both DataFrames are the same
    min_length = min(len(aligned_sensor_df), len(aligned_hypnogram_df))
    aligned_sensor_df = aligned_sensor_df.iloc[:min_length]
    aligned_hypnogram_df = aligned_hypnogram_df.iloc[:min_length]

    return aligned_sensor_df, aligned_hypnogram_df


def resample_features(acc_df, gyro_df, cfg):
    """
    Resamples sensor features to match the wanted frequency (usually hypnogram's 30-second epochs).
    Keeps 'body_pos' as discrete by forwarding the last known value.
    """
    if cfg is not None:
        sample_interval = cfg['time_resolution']
    else:
        sample_interval = '30s'


    resampled_gyro_df = gyro_df.resample(sample_interval).mean().interpolate(method='spline', order=3, s=0.)
    resampled_acc_df = acc_df.resample(sample_interval).mean().interpolate(method='spline', order=3, s=0.)
    resampled_acc_df = resampled_acc_df.reindex(resampled_gyro_df.index).interpolate(method='spline', order=3, s=0.)
    feature_df = pd.concat([resampled_acc_df, resampled_gyro_df], axis=1)

    print(feature_df.columns)
    if 'body_pos' in feature_df.columns:
        print("rounding...")
        feature_df['body_pos'] = feature_df['body_pos'].apply(lambda x: int(x))

    return feature_df


def rename_columns(df, format):
    """
    Renames the columns of the feature dataframe according to standard convention.
    """
    if format == 'legacy':
        df.rename(columns={'feature1(class N)':'body_pos', 'feature2(m/sec)': 'activity',
                    'feature7(m/sec^2)':'actigraph', 'feature3_X(unitless)': 'acf_max_x',
                    'feature3_Y(unitless)': 'acf_max_y','feature4_X(Hz)': 'resp_rate_x',
                    'feature4_Y(Hz)': 'resp_rate_y','feature5_Y(grad/sec)': 'resp_peak_median',
                    'feature6_Y(grad/sec)': 'resp_peak_std'}, inplace=True)
    else:
        df.rename(columns={'BodyPosValue':'body_pos', 'ActivityValue':'activity', 
                    'ActigraphValue':'actigraph', 'ACFMaxValue_X':'acf_max_x',
                    'ACFMaxValue_Y':'acf_max_y', 'RespRate_X':'resp_rate_x', 'RespRate_Y':'resp_rate_y',
                    'RespPeakMed_Y':'resp_peak_median', 'RespPeakStd_Y':'resp_peak_std'}, inplace=True)
    return df


def select_default_features(features, format='standard'):
    """
    Selects the default 5 features for classification.
    """

    if type(features) == pd.DataFrame and format == 'legacy':
        features = features[['feature2(m/sec)','feature3_Y(unitless)','feature4_Y(Hz)',
                             'feature5_Y(grad/sec)', 'feature6_Y(grad/sec)']]
    elif type(features) == pd.DataFrame and format == 'new':
        features = features[['ActivityValue','ACFMaxValue_Y','RespRate_Y',
                             'RespPeakMed_Y', 'RespPeakStd_Y']]
        
    elif type(features) == pd.DataFrame and format == 'standard':
        features = features[['activity','acf_max_y','resp_rate_y','resp_peak_median', 'resp_peak_std']]
    return features

def read_and_process_features(acc_path, gyro_path, time_offset, cfg=None):
    """
    Reads sensor features from CSV files and processes them for classification.
    
    Args:
        acc_path (str): Path to the accelerometer feature CSV file.
        gyro_path (str): Path to the gyroscope feature CSV file.
        time_offset (int): Time offset from UTC in hours.
    
    Returns:
        pd.DataFrame: A DataFrame with sensor features ready for classification.
    """

    file = open(acc_path, 'r')
    first_line = file.readline()
    file.close()

    # Legacy csv format
    if 'UTCTimestamp(ms)' in first_line:
        skiprows = 0
        skipfooter = 0
        unit = 'ms'
        timeColName = 'UTCTimestamp(ms)'
        format = 'legacy'
    else: # New format
        skiprows = 1
        skipfooter = 4
        unit = 's'
        timeColName = 'Timestamp'
        format = 'new'

    accData = pd.read_csv(acc_path, skipinitialspace=True, skiprows=skiprows, skipfooter=skipfooter, engine='python')
    gyroData = pd.read_csv(gyro_path, skipinitialspace=True, header=skiprows, skipfooter=skipfooter, engine='python')
    
    # Convert timestamps to local time using the time offset
    accTime  = pd.to_datetime(accData[timeColName],  unit=unit, utc=True) + pd.Timedelta(hours=time_offset)
    gyroTime = pd.to_datetime(gyroData[timeColName], unit=unit, utc=True) + pd.Timedelta(hours=time_offset)

    # Set time based indexing and drop the now redundant time columns
    accData = accData.set_index(accTime).drop(columns=[timeColName])
    gyroData = gyroData.set_index(gyroTime).drop(columns=[timeColName])
    
    # Rename columns for clarity.
    accData  = rename_columns(accData, format)
    gyroData = rename_columns(gyroData, format)

    # Resample features to constant 30s to match hypnogram
    feature_df = resample_features(accData, gyroData, cfg=cfg)
    feature_df.index.name = 'timestamp'
    
    if cfg is not None:
        if cfg['default_features']:
            feature_df = select_default_features(feature_df, format='standard')

    return feature_df


def read_subject_info(info_path):
    """
    Reads subject information from a JSON file.

    Args:
        info_path (str): Path to the subject info JSON file.
    
    Returns:
        dict: A dictionary containing subject information.
    """
    with open(info_path, 'r') as file:
        subject_info = json.load(file)
    return subject_info[0]


def compile_recording(acc_path, gyro_path, hypno_path, info_path, cfg):
    """
    Compiles a single sleep recording from sensor and hypnogram data.

    Args:
        acc_path (str): Path to the accelerometer data file.
        gyro_path (str): Path to the gyroscope data file.
        hypno_path (str, optional): Path to the hypnogram data file.
        info_path (str, optional): Path to the subject info file.
    
    Returns:
        SleepRecording: An instance of SleepRecording with features and labels.
    """
    # Read subject info from JSON file
    if info_path:
        subject_info = read_subject_info(info_path)
    else:
        subject_info = {}
    
    if subject_info.get('subject_age') == None:
        age=1
    else:
        age=subject_info.get('subject_age')
    
    if subject_info.get('location'):
        time_zone=subject_info.get('location')
    else:
        time_zone='Europe/Helsinki'

    # Load feature data
    sensor_features_df = read_and_process_features(acc_path, gyro_path,
                                                    time_zone=time_zone, cfg=cfg)

    # Load hypnogram data
    hypnogram_df = read_and_process_hypnogram(hypno_path, cfg=cfg)

    # Align sensor features with hypnogram labels
    #if not raw_format:
    sensor_features_df, hypnogram_df = align_features_with_labels(sensor_features_df,
                                                                hypnogram_df,
                                                                cfg=cfg)

    # Convert data to numpy arrays
    features = sensor_features_df
    labels   = hypnogram_df

    compiledRecording = SleepRecording(
            features    = features,
            labels      = labels,
            id          = subject_info.get('subject_id'),
            clinical_id = subject_info.get('clinical_id'),
            age         = age,
            comments    = subject_info.get('comments')
        )
    return compiledRecording


def scan_directory(path, cfg):
    """
    Scans a directory for accelerometer, gyroscope, hypnogram and info files.
    
    Args:
        path (str): Directory path to scan.
    
    Returns:
        Tuple: Paths to the accelerometer, gyroscope, and hypnogram and subject info files.
    """
    acc_file, gyro_file, hypno_file, info_file = None, None, None, None

    for file in os.listdir(path):
        if file.endswith('.csv') and 'AccFeatures' in file:
                acc_file = file
        elif file.endswith('.csv') and 'GyroFeatures' in file:
                gyro_file = file
        elif (('sleep' in file) or ('profile' in file) or ('hypnogram' in file)):
            hypno_file = file
        elif file.endswith('.json'):
            info_file = file
        else:
            continue

    return (acc_file, gyro_file, hypno_file, info_file)


def create_dataset(root, cfg={'default_features':True, 'time_resolution':'30s'}):
    """
    Creates a dataset by scanning a parent directory for subdirectories containing all relevant sleep recording files.
    
    Args:
        root (str): The root directory containing subdirectories of sleep recordings.
    
    Returns:
        NappaDataset: A dataset containing multiple SleepRecording instances.
    """ 

    directories = [entry.name for entry in os.scandir(root) if entry.is_dir()]
    recordings = []

    for directory in directories:

        path = os.path.join(root, directory)
        
        acc_file, gyro_file, hypno_file, info_file = scan_directory(path, cfg=cfg)
        if None in [acc_file, gyro_file, hypno_file, info_file]:
            continue
            
        recording = compile_recording(acc_path  =os.path.join(path, acc_file),
                                      gyro_path =os.path.join(path, gyro_file),
                                      hypno_path=os.path.join(path, hypno_file),
                                      info_path =os.path.join(path, info_file),
                                      cfg=cfg)
        recordings.append(recording)


    return NappaDataset(data=recordings)