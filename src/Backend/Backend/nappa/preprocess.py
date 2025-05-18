import copy
import numpy as np
import pandas as pd
import torch

from nappa.objects import NappaDataset


class StandardScaler:
    """
    A class to perform feature scaling using z-score normalization.
    """

    def __init__(self, method='global'):
        self.method = method
        if self.method not in ['global', 'subjectwise']:
            raise ValueError('Method must be either "global" or "subjectwise".')

    def transform(self, features, mean, std):
        features = (features - mean) / std
        return features

    def __call__(self, data, with_mean=None, with_std=None):
        """
        Applies the scaling transformation to the data.

        Args:
            data (NappaDataset or np.ndarray / torch.tensor): The dataset or features to normalize.
            with_mean: The mean values from the training set for global scaling.
            with_std: The standard deviation values from the training set for global scaling.

        Returns:
            data (NappaDataset or np.ndarray / torch.tensor): A new instance of the normalized data
        """
        copy_data = copy.deepcopy(data)
        if isinstance(data, np.ndarray) or isinstance(data, pd.DataFrame):
            if self.method == 'global':
                copy_data = self.transform(copy_data, with_mean, with_std)
            else:
                copy_data = self.transform(copy_data, copy_data.mean(axis=0), copy_data.std(axis=0))

        elif isinstance(data, NappaDataset):
            if data.normalization is not None:
                raise ValueError('Data already normalized.')

            if type(data.features) == torch.Tensor:
                global_mean = with_mean if with_mean is not None else torch.mean(data.features, dim=0)
                global_std = with_std if with_mean is not None else torch.std(data.features, dim=0)
            else:
                global_mean = with_mean if with_mean is not None else np.mean(data.features, axis=0)
                global_std = with_std if with_mean is not None else np.std(data.features, axis=0)

            # Normalize each recording in the dataset
            for rec in copy_data:
                if self.method == 'global':
                    mean = global_mean
                    std = global_std
                else:
                    # Subject-wise normalization
                    if type(data.features) == torch.Tensor:
                        mean = torch.mean(rec.features, dim=0)
                        std = torch.std(rec.features, dim=0)
                    else:
                        mean = rec.features.mean(axis=0)
                        std = rec.features.std(axis=0)

                rec.features = self.transform(rec.features, mean, std)
            
            copy_data.normalization = f'standard ({self.method})'

        else:
            raise ValueError('Data must be a NappaDataset or a numpy array.')
        return copy_data # Return a copy of the normalized data, do not modify in-place for safety.