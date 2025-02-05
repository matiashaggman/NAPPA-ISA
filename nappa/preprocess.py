import copy
import numpy as np

from .objects import NappaDataset

class StandardScaler:
    """
    A class to perform feature scaling using z-score normalization.
    """

    def __init__(self, method='global'):
        """
        Initializes the HybridScaler with a specified scaling method.

        Args:
            method (str): The method used for scaling, either 'global' for global scaling or 'subjectwise' for individual subject scaling.
        """
        self.method = method
        if self.method not in ['global', 'subjectwise']:
            raise ValueError('Method must be either "global" or "subjectwise".')

    def transform(self, features, mean, std):
        """
        Transforms the features using z-score normalization.

        Args:
            features (np.ndarray): The features to scale.
            mean (np.ndarray): The mean values used for z-score normalization.
            std (np.ndarray): The standard deviation values used for z-score normalization.
        
        Returns:
            np.ndarray: The scaled features.
        """

        # Apply z-score normalization for the sensor features
        features = (features - mean) / std

        return features

    def __call__(self, data, with_mean=None, with_std=None):
        """
        Applies the scaling transformation to the data.

        Args:
            data (NappaDataset or np.ndarray): The dataset or features to normalize.
            is_testset (bool): Indicates if the data is a test set, which uses global scaling parameters.
            with_mean (np.ndarray): The mean values from the training set for global scaling.
            with_std (np.ndarray): The standard deviation values from the training set for global scaling.

        Returns:
            NappaDataset: The normalized dataset.
        """
        copy_data = copy.deepcopy(data)
        if isinstance(data, np.ndarray):
            if self.method == 'global':
                copy_data = self.transform(copy_data, with_mean, with_std)
            else:
                copy_data = self.transform(copy_data, copy_data.mean(axis=0), copy_data.std(axis=0))
        
        elif isinstance(data, NappaDataset):
            if data.normalization is not None:
                raise ValueError('Data already normalized.')

            # Use global mean and std if it's a test set, otherwise calculate from dataset
            global_mean = with_mean if with_mean is not None else data.features.mean(axis=0)
            global_std = with_std if with_mean is not None else data.features.std(axis=0)
            
            # Normalize each recording in the dataset
            for rec in copy_data:
                if self.method == 'global':
                    mean = global_mean
                    std = global_std
                else:
                    # Subject-wise normalization
                    mean = rec.features.mean(axis=0)
                    std = rec.features.std(axis=0)

                rec.features = self.transform(rec.features, mean, std)
            
            copy_data.normalization = f'standard ({self.method})'

        return copy_data
