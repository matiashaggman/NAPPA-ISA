import numpy as np
import pandas as pd
import torch
import pickle

class SleepRecording:
    """
    A class to represent a single sleep recording. 
    """
    def __init__(self, features, labels=None, wear_idx=None, clinical_id=None, serial_number=None, comments=None,
                       id=None,  age=None,    timestamps=None,  sampling_interval=None):
        """
        Initialize a SleepRecording object.

        Args:
          features (pd.Dataframe or torch.Tensor): Sensor data representing the features extracted from the sleep recording.
          labels (pd.Dataframe or torch.Tensor, optional): The labels corresponding to each epoch in the sleep recording.
          wear_idx (pd.Series, optional): The time-indexed points where sensor was worn on the baby.
          id (int, optional): A unique identifier for the subject of the sleep recording.
          age (int, optional): The age of the subject in months.
          timestamps (np.ndarray, optional): Timestamps corresponding to each epoch in the sleep recording.
          sampling_interval (float, optional): The time interval between data points in the recording.
        """
        self.id = id
        self.clinical_id = clinical_id
        self.serial_number = serial_number
        self.age = age
        self.features = features
        self.labels = labels
        self.wear_idx = wear_idx
        self.timestamps = timestamps
        self.comments = comments
        self.sampling_interval = sampling_interval

        if type(features) == pd.DataFrame:
            if type(features.index) == pd.DatetimeIndex:
                self.timestamps = self.features.index
                self.start = features.index[0]
                self.end = features.index[-1]
                self.duration = self.end - self.start
                self.mode = 'default'  
        else:
            self.timestamps = np.arange(start=0, stop=self.features.shape[0]*30, step=30)
            self.mode = 'torch'

        return
    
    def save(self, filename: str, precision: int = 3):
        """
        Save the contents (features, labels) of the sleep recording as a .csv file.
        """
        if self.mode == 'default':
            df = pd.concat([self.features, self.labels], axis=1)
            df.to_csv(filename, date_format='%Y-%m-%d %H:%M:%S', float_format=f'%.{precision}f')
        else:
            raise ValueError("Cannot save torch tensor data.")

    def __str__(self) -> str:
        ret = [
            f'Subject ID: {self.id}\n' if self.id is not None else '',
            f'Clinical ID: {self.clinical_id}\n' if self.clinical_id is not None else '',
            f'Serial number: {self.serial_number}\n' if self.serial_number is not None else '',
            f'Age: {self.age} months\n' if self.age is not None else '',
            f'Number of data points: {self.features.shape[0]}\n',
            f'Duration: {self.duration}\n' if hasattr(self, 'duration') else '',
        ]
        return ''.join(ret)
    
    def __len__(self) -> int:
        return self.features.shape[0]

    
class NappaDataset(torch.utils.data.Dataset):
    """
    A dataset class to hold multiple SleepRecording objects.
    Compatible with torch dataloader & batched processing.
    """
    def __init__(self, data):
        """
        Initialize a NappaDataset object.

        Args:
          data (list or str): If list, should contain SleepRecording objects.
            If str, should be the path to a pickled file of the dataset.
        """
        self.normalization = None
        
        self.recordings = []

        if all(isinstance(item, SleepRecording) for item in data):
            self.recordings = data
        elif isinstance(data, str) and data.endswith('.pkl'):
            with open(data, 'rb') as f:
                obj = pickle.load(f)
            self.__dict__.update(obj.__dict__)
        else:
            raise ValueError("Data must be a list of SleepRecording instances or a path to a pickled NappaDataset object.")

        if type(self.recordings[0].features) == torch.Tensor:
            self.mode = 'torch'
        else:
            self.mode = 'default'
        return None

    @property
    def features(self):
        """
        Returns a concatenated numpy array of features from all SleepRecording objects in the dataset.
        """
        if self.mode == 'torch':
            return torch.cat([rec.features for rec in self.recordings], dim=0)
        else:
            return pd.concat([rec.features for rec in self.recordings], axis=0)

    @property
    def labels(self):
        """
        Returns a concatenated numpy array of labels from all SleepRecording objects in the dataset.
        """
        if self.mode == 'torch':
            return torch.cat([rec.labels for rec in self.recordings], dim=0)
        else:
            return pd.concat([rec.labels for rec in self.recordings], axis=0)

    @property
    def ids(self) -> np.ndarray:
        """
        Returns a numpy array of subject IDs from all SleepRecording objects in the dataset.
        """
        return np.array([rec.id for rec in self.recordings])

    @property
    def ages(self) -> np.ndarray:
        """
        Returns a numpy array of subject ages from all SleepRecording objects in the dataset.
        """
        return np.array([rec.age for rec in self.recordings])

    def to_torch(self):
        """
        Set the dataset to training mode by converting data to torch.tensors.
        """
        self.mode = 'torch'
        for rec in self.recordings:
            rec.mode = 'torch'
            if type(rec.features) == pd.DataFrame:
                rec.features = torch.tensor(rec.features.to_numpy(), dtype=torch.float32)
                rec.labels = torch.tensor(rec.labels.to_numpy(), dtype=torch.long)
        return self

    def save(self, filename: str):
        """
        Save the dataset to a pickle file.

        Args:
          filename (str): The path where the dataset should be saved.
        """
        if filename.endswith('.pkl'):
            with open(filename, 'wb') as f:
                pickle.dump(self, f)
        else:
            raise ValueError("Unsupported file format. Use .pkl for saving.")

    def selectFeatures(self, features: list):
        """
        Select a subset of features from the dataset based on a list of indices (or feature names).

        Args:
          indices (list): The indices of the features to select.

        Returns:
          NappaDataset: The dataset with the selected features.
        """
        if self.mode == 'torch':
            for rec in self.recordings:
                rec.features = rec.features[:, features]
        else:
            if type(features[0]) == int:
                for rec in self.recordings:
                    rec.features = rec.features.iloc[:, features]
            elif type(features[0]) == str:
                for rec in self.recordings:
                    rec.features = rec.features.loc[:, features]
        return self

    def setSubjectAges(self, ages: dict):
        """
        Update the ages for subjects based on a provided mapping from ID to age.

        Args:
          ages (dict): A dictionary mapping subject ID to age in months.

        Returns:
          NappaDataset: The dataset with updated ages.
        """
        for subject in self.recordings:
            subject.age = ages.get(subject.id, subject.age)
        return self

    def labelsToNumeric(self, mapping={'N3': 0, 'N2': 0, 'Deep':0,
                                    'N1': 1, 'REM': 1, 'Light': 1,
                                    'Wake': 2, 'A':3}):
        """
        Convert string labels (Sleep stages 'N3', 'N2', etc.) to numeric labels based on a provided mapping.
        Default: N3/N2 (Deep sleep): 0, N1/REM (Light sleep): 1, Wake: 2

        Args:
        mapping (dict): A dictionary mapping string labels to numeric labels.

        Returns:
        NappaDataset: The dataset with numeric labels.
        """
        if not self.mode == 'torch':
            for rec in self.recordings:
                rec.labels = rec.labels.replace(mapping)
                rec.labels = rec.labels.infer_objects(copy=False)
                    
        return self


    def getById(self, id) -> SleepRecording:
        """
        Retrieve a SleepRecording by subject ID.

        Args:
        id (int): The subject ID.

        Returns:
        SleepRecording: The recording corresponding to the given ID, or None if not found.
        """
        return next((rec for rec in self.recordings if rec.id == id))

    def dropById(self, id):
        """
        Remove a SleepRecording from the dataset by ID.

        Args:
          id (int): The subject ID.

        Returns:
          NappaDataset: The dataset with the specified recording removed.
        """
        if type(id) == int:
            self.recordings = [rec for rec in self.recordings if rec.id != id]
        elif type(id) == list:
            self.recordings = [rec for rec in self.recordings if rec.id not in id]
        return self

    def sortById(self):
        """
        Sort the dataset by subject ID.

        Returns:
          NappaDataset: The sorted dataset.
        """
        self.recordings.sort(key=lambda recording: recording.id)
        return self

    def sortByLength(self):
        """
        Sort the dataset by the length of the recordings.

        Returns:
          NappaDataset: The sorted dataset.
        """
        self.recordings.sort(key=lambda recording: len(recording))
        return self
    
    def sortByAge(self):
        """
        Sort the dataset by the length of the recordings.

        Returns:
          NappaDataset: The sorted dataset.
        """
        self.recordings.sort(key=lambda recording: recording.age)
        return self
    
            
    def __len__(self):
        return len(self.recordings)
    
    def __getitem__(self, index):
        return self.recordings[index]
    
    def __str__(self):
        ret = [
            f'Number of sleep recordings: {len(self)}\n',
            f'Subject age range: {np.min(self.ages)} - {np.max(self.ages)} (months) \n' if None not in self.ages  else '',
            f'Number of data points: {self.features.shape[0]}\n',
            f'Number of features: {self.features.shape[1]}\n',
            f'Mode: {self.mode}\n',
            f'Normalization: {self.normalization}\n']
        return ''.join(ret)