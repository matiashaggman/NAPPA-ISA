import os
import json
import pandas as pd

from nappa.objects import NappaDataset, SleepRecording

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

    if 'body_pos' in feature_df.columns:
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


def read_and_process_features(acc_path, gyro_path, time_offset=None, time_zone=None, cfg=None):
    """
    Reads sensor features from CSV files and processes them for classification.
    Either time_offset or time_zone must be provided, but not both.
    """
    if (time_offset is None and time_zone is None) or (time_offset is not None and time_zone is not None):
        raise ValueError("Exactly one of time_offset or time_zone must be specified.")

    file = open(acc_path, 'r')
    first_line = file.readline()
    file.close()

    # Legacy csv format
    if 'UTCTimestamp(ms)' in first_line:
        skiprows = 0
        skipfooter = 0
        unit = 'ms'
        time_col_name = 'UTCTimestamp(ms)'
        fmt = 'legacy'
    else:  # New format
        skiprows = 1
        skipfooter = 4
        unit = 's'
        time_col_name = 'Timestamp'
        fmt = 'new'

    acc_data = pd.read_csv(acc_path, skipinitialspace=True, skiprows=skiprows, skipfooter=skipfooter, engine='python')
    gyro_data = pd.read_csv(gyro_path, skipinitialspace=True, header=skiprows, skipfooter=skipfooter, engine='python')

    acc_time = pd.to_datetime(acc_data[time_col_name], unit=unit, utc=True)
    gyro_time = pd.to_datetime(gyro_data[time_col_name], unit=unit, utc=True)
    if time_zone:
        acc_time = acc_time.dt.tz_convert(time_zone).dt.tz_localize(None)
        gyro_time = gyro_time.dt.tz_convert(time_zone).dt.tz_localize(None)
    else:
        acc_time = acc_time.dt.tz_localize(None) + pd.Timedelta(hours=time_offset)
        gyro_time = gyro_time.dt.tz_localize(None) + pd.Timedelta(hours=time_offset)

    acc_data = acc_data.set_index(acc_time).drop(columns=[time_col_name])
    gyro_data = gyro_data.set_index(gyro_time).drop(columns=[time_col_name])

    acc_data = rename_columns(acc_data, fmt)
    gyro_data = rename_columns(gyro_data, fmt)

    feature_df = resample_features(acc_data, gyro_data, cfg=cfg)
    feature_df.index.name = 'timestamp'

    if cfg and cfg.get('default_features'):
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
    return subject_info


def compile_recording(acc_path, gyro_path, cfg, hypno_path=None, analyzed_path=None, info_path=None):
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
       
    if subject_info.get('location'):
        time_zone=subject_info.get('location')
    else:
        time_zone='Europe/Helsinki'

    # Load feature data
    sensor_features_df = read_and_process_features(acc_path, gyro_path,
                                                    time_zone=time_zone, cfg=cfg)

    # Load hypnogram data
    if hypno_path:
        hypnogram_df = read_and_process_hypnogram(hypno_path, cfg=cfg)

        # Align sensor features with hypnogram labels
        sensor_features_df, hypnogram_df = align_features_with_labels(sensor_features_df,
                                                                hypnogram_df,
                                                                cfg=cfg)
        labels = hypnogram_df

    if analyzed_path:
        analyzed_df = pd.read_csv(analyzed_path)
        analyzed_df['timestamp'] = pd.to_datetime(analyzed_df['timestamp'])
        analyzed_df = analyzed_df.set_index('timestamp')
        labels = analyzed_df[['sleep_stage', 'sdt']]    
        
    
    compiledRecording = SleepRecording(
            features    = sensor_features_df,
            labels      = labels if hypno_path or analyzed_path else None,
            id          = subject_info.get('subject_id') if 'subject_id' in subject_info else None,
            clinical_id = subject_info.get('clinical_id') if 'clinical_id' in subject_info else None,
            age         = subject_info.get('subject_age') if 'subject_age' in subject_info else None,
            comments    = subject_info.get('comments') if 'comments' in subject_info else None,
        )
    return compiledRecording


def scan_directory(path):
    """
    Recursively scans a directory and its subdirectories for accelerometer, gyroscope, hypnogram, and info files.
    
    Args:
        path (str): Directory path to scan.
    
    Returns:
        Tuple: Paths to the accelerometer, gyroscope, hypnogram, and subject info files.
    """
    acc_files, gyro_files, hypno_files, analyzed_files, info_files = [], [], [], [], []

    # Walk through all subdirectories and files
    for root, _, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            if file.endswith('.csv') and 'AccFeatures' in file:
                acc_files.append(full_path)
            elif file.endswith('.csv') and 'GyroFeatures' in file:
                gyro_files.append(full_path)
            elif 'sleep' in file or 'profile' in file or 'hypnogram' in file:
                hypno_files.append(full_path)
            elif 'Analyzed' in file:
                analyzed_files.append(full_path)
            elif file.endswith('.json'):
                info_files.append(full_path)

    return (acc_files, gyro_files, hypno_files, analyzed_files, info_files)


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
        
        acc_files, gyro_files, hypno_files, analyzed_files, info_files = scan_directory(path)
        if len(acc_files) == 0 or len(gyro_files) == 0:
            # Skip if accelerometer or gyroscope files are not found
            print(f"Skipping directory {directory}: Missing accelerometer or gyroscope files.")
            continue
        
        info_file = os.path.join(path, info_files[0]) if info_files else None

        for i in range(len(acc_files)):
            acc_file = os.path.join(path, acc_files[i])
            gyro_file = os.path.join(path, gyro_files[i])
            hypno_file = os.path.join(path, hypno_files[i]) if hypno_files else None
            analyzed_file = os.path.join(path, analyzed_files[i]) if analyzed_files else None

            recording = compile_recording(acc_path=acc_file,
                                        gyro_path =gyro_file,
                                        hypno_path=hypno_file,
                                        analyzed_path=analyzed_file,
                                        info_path =info_file,
                                        cfg=cfg)
            recordings.append(recording)


    return NappaDataset(data=recordings)