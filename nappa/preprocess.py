import copy
import numpy as np
from scipy.stats import linregress

from .objects import NappaDataset

class HybridScaler:
    """
    A class to perform feature scaling using a hybrid method that combines
    z-score normalization with heuristic adjustments for specific features.
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
        Transforms the features using heuristic scaling and z-score normalization.

        Args:
            features (np.ndarray): The features to scale.
            mean (np.ndarray): The mean values used for z-score normalization.
            std (np.ndarray): The standard deviation values used for z-score normalization.
        
        Returns:
            np.ndarray: The scaled features.
        """
        # Apply heuristic scaling for activity feature
        mask = features[:, 0] <= 0.5
        features[mask, 0] = (features[mask, 0] - 0.5) / 0.5
        features[~mask, 0] = 1 + np.log2(features[~mask, 0])

        # Apply heuristic scaling for autocorrelation feature
        features[:, 1] = (features[:, 1] - 0.5) / 0.5

        # Apply z-score normalization for the rest of the sensor features
        features[:, 2:] = (features[:, 2:] - mean[2:]) / std[2:]

        return features

    def __call__(self, data, with_mean=None, with_std=None):
        """
        Applies the scaling transformation to the data.

        Args:
            data (NappaDataset or np.ndarray): The dataset or features to normalize.
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
            global_std = with_std if with_std is not None else data.features.std(axis=0)
            
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
            
            copy_data.normalization = f'hybrid ({self.method})'

        return copy_data

class CustomScaler:
    """
    A class to perform feature scaling using a hybrid method that combines
    z-score normalization with heuristic adjustments for specific features.
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
        Transforms the features using heuristic scaling and z-score normalization.

        Args:
            features (np.ndarray): The features to scale.
            mean (np.ndarray): The mean values used for z-score normalization.
            std (np.ndarray): The standard deviation values used for z-score normalization.
        
        Returns:
            np.ndarray: The scaled features.
        """
        features[:, 0] = np.log(np.log(features[:, 0]) + 3)
        features[:, 1] = np.log(features[:, 1] + 1)
        features[:, 2] = (features[:, 2] - mean[2])/std[2]
        features[:, 3] = np.log(features[:, 3] + 1)
        features[:, 4] = np.log(features[:, 4])

        features = (features - np.mean(features, axis=0))/np.std(features, axis=0)

        return features

    def __call__(self, data, with_mean=None, with_std=None):
        """
        Applies the scaling transformation to the data.

        Args:
            data (NappaDataset or np.ndarray): The dataset or features to normalize.
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
            global_std = with_std if with_std is not None else data.features.std(axis=0)
            
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
            
            copy_data.normalization = f'log ({self.method})'

        return copy_data

class RobustScaler:
    """
    A class to perform feature scaling using a hybrid method that combines
    z-score normalization with heuristic adjustments for specific features.
    """
    def __iqr(self, x):
        return np.subtract(*np.percentile(x, [75, 25], axis=0))

    def __init__(self, method='global'):
        """
        Initializes the HybridScaler with a specified scaling method.

        Args:
            method (str): The method used for scaling, either 'global' for global scaling or 'subjectwise' for individual subject scaling.
        """
        self.method = method
        if self.method not in ['global', 'subjectwise']:
            raise ValueError('Method must be either "global" or "subjectwise".')

    def transform(self, features, median, iqr):
        """
        Transforms the features using robust scaling

        Args:
            features (np.ndarray): The features to scale.
            mean (np.ndarray): The median values used for scaling.
            std (np.ndarray): The interquartile range values used for scaling.
        
        Returns:
            np.ndarray: The scaled features.
        """
        epsilon = 0.001
        adjusted_iqr = np.where(iqr == 0, epsilon, iqr)

        features = (features - median) / adjusted_iqr

        return features

    def __call__(self, data, with_median=None, with_iqr=None):
        """
        Applies the scaling transformation to the data.

        Args:
            data (NappaDataset or np.ndarray): The dataset or features to normalize.
            with_mean (np.ndarray): The mean values from the training set for global scaling.
            with_std (np.ndarray): The standard deviation values from the training set for global scaling.

        Returns:
            NappaDataset: The normalized dataset.
        """
        copy_data = copy.deepcopy(data)
        if isinstance(data, np.ndarray):
            if self.method == 'global' and with_median is not None and with_iqr is not None:
                copy_data = self.transform(copy_data, with_median, with_iqr)
            else:
                copy_data = self.transform(copy_data, np.median(copy_data, axis=0), self.__iqr(copy_data))
        
        elif isinstance(data, NappaDataset):
            if data.normalization is not None:
                raise ValueError('Data already normalized.')

            # Use global mean and std if it's a test set, otherwise calculate from dataset
            global_median = with_median if with_median is not None else np.median(data.features, axis=0)
            global_iqr = with_iqr if with_iqr is not None else self.__iqr(data.features)
            
            # Normalize each recording in the dataset
            for rec in copy_data:
                if self.method == 'global':
                    median = global_median
                    iqr = global_iqr
                else:
                    # Subject-wise normalization
                    median = np.median(rec.features, axis=0)
                    iqr = self.__iqr(rec.features)

                rec.features = self.transform(rec.features, median, iqr)
            
            copy_data.normalization = f'Robust ({self.method})'

        return copy_data

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

class AgeAdjuster:

    def __init__(self, age_as_feature=False, age_control_features=[], feature_interactions=[]):
        self.age_as_feature = age_as_feature
        self.age_control_features = age_control_features
        self.feature_interactions = feature_interactions

    def setAgeAsFeature(self, dataset:NappaDataset) -> NappaDataset:
        for rec in dataset.recordings:
            age_feature_column = np.full((rec.features.shape[0], 1), rec.age)

            features_with_age = np.concatenate((rec.features, age_feature_column), axis=1)               
            rec.features = features_with_age
        
        return dataset
        
    def featureInteraction(self, dataset, feature_indices) -> NappaDataset:
        for rec in dataset:
            for i in feature_indices:
                interaction_feature = rec.features[:, i] * rec.age
                rec.features = np.concatenate([rec.features , interaction_feature.reshape(-1,1)], axis=1)
        return dataset

    def subtract_age_estimates(self, dataset, feature_indices) -> NappaDataset:
        for i in feature_indices:
            # Compute the mean values for this feature for all subjects in the dataset
            feature_mean_values = np.array([np.mean(rec.features[rec.features[:, i] > 0, i]) for rec in dataset.recordings])
            # Linear fit to age vs feature mean value
            res = linregress(dataset.ages, feature_mean_values)     

            for rec in dataset.recordings: 
                rec.features[:, i] = rec.features[:, i] - (res.intercept + res.slope*rec.age)

        return dataset

    def __call__(self, dataset:NappaDataset) -> NappaDataset:
        copy_dataset = copy.deepcopy(dataset)
        if self.age_as_feature:
            copy_dataset = self.setAgeAsFeature(copy_dataset)
        if len(self.age_control_features) > 0:
            copy_dataset = self.subtract_age_estimates(copy_dataset, self.age_control_features)
        if len(self.feature_interactions) > 0:
            copy_dataset = self.featureInteraction(copy_dataset, self.feature_interactions)
        return copy_dataset