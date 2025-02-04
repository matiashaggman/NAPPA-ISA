import os
import torch
import torch.nn as nn
from concurrent.futures import ProcessPoolExecutor

from xlstm import (
    xLSTMBlockStack,
    xLSTMBlockStackConfig,
    mLSTMBlockConfig,
    mLSTMLayerConfig,
    sLSTMBlockConfig,
    sLSTMLayerConfig,
    FeedForwardConfig,
)

class NappaModel(nn.Module):
    def predict(self, x: torch.Tensor) -> torch.Tensor:
        """
        Predict labels for the given features of a sleep recording.

        Args:
            x (Tensor): The feature matrix of a sleep recording.

        Returns:
            Tensor: Probability distribution of the classes at each time step and the predicted classes.
        """
        self.eval()
        with torch.no_grad():
            output = self.forward(x)

            # Predicted probability distribution on classes for each timestep
            p_dist = torch.softmax(output, dim=-1)
            
            # Predicted class for each timestep (integer)
            p_classes = torch.argmax(p_dist, dim=-1)

        return torch.cat([p_classes.unsqueeze(-1), p_dist], dim=1)

    def load(self, weight_file: str):
        self.load_state_dict(torch.load(weight_file, map_location=self.device, weights_only=True))
        return self

    def reset(self):
        """
        Reset the parameters of the model.
        """
        for layer in self.children():
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()
        return self

    @property
    def device(self) -> torch.device:
        return next(self.parameters()).device

    @property
    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)  



class NappaXLSTM(nn.Module):
    def __init__(self, num_features=5, num_classes=3, num_blocks=1, num_heads=1, context_length=1200):

        super().__init__()
        self.name = 'NappaXLSTM'

        cfg = xLSTMBlockStackConfig(

            mlstm_block=mLSTMBlockConfig(
                mlstm=mLSTMLayerConfig(
                    conv1d_kernel_size=2,
                    qkv_proj_blocksize=2,
                    num_heads=num_heads
                )
            ),
            context_length=1200,
            num_blocks=num_blocks,
            embedding_dim=num_features,
        )

        self.model = xLSTMBlockStack(cfg)
        self.out = nn.Linear(in_features=num_features, out_features=num_classes)

    def forward(self, x:torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
          x (Tensor): The input tensor containing features of shape (batch_size, rec_length, num_features).
          rec_lengths (Tensor): The actual lengths of each sleep sequence before padding.

        Returns:
          Tensor: The output logits of shape (batch_size, rec_length, n_classes).
        """
        # Pass the input through the xlstm.   
        x = self.model(x)
        
        # Pass the output of the layer through the output layer to get class logits for each time step.
        y = self.out(x)
        
        return y

    def predict(self, x:torch.Tensor) -> torch.Tensor:
        """
        Predict labels for given features of a sleep recording.

        Args:
          Features (Tensor): The feature matrix of a sleep recording.

        Returns:
          Predictions (Tensor): probability distribution of the sleep classes at each time step
          and the class indices with highest probability on the first column. A tensor of shape (rec_length, num_classes + 1)
        """
        self.eval()
        with torch.no_grad():
            output = self.forward(x)#.reshape(-1, self.n_classes)

            p_dist = torch.softmax(output, dim=-1) # Predicted probability distribution on sleep stages per each timestep
            p_classes = torch.argmax(p_dist, dim=-1) # Predicted class for each timestep (integer)

        return torch.cat([p_classes.transpose(0,1), p_dist.squeeze(0)], dim=1)
    
    def load(self, weight_file:str):
        self.load_state_dict(torch.load(weight_file, map_location=self.device, weights_only=True))
        return self

    def reset(self):
        """
        Reset the parameters of the model. This is called before training a new model instance in LOSOCV.
        """
        for layer in self.children():
            if hasattr(layer, 'reset_parameters'):
                layer.reset_parameters()
        return self

    @property
    def device(self) -> torch.device:
        return next(self.parameters()).device
    
    @property
    def num_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    

class NappaSleepNet(NappaModel):
    def __init__(self, num_features=5, num_classes=3, hidden_size=10, num_layers=2,
                  bidirectional=True, name='NappaSleepNet'):
        """
        Initialize the NappaSleepNet model for classifying sleep stages.
        # NOTE: The model is initialized by default with the same hyperparameters as used in the article
         https://doi.org/10.1016/j.heliyon.2024.e33295
        Args:
          n_features (int): The number of features for each time step in the input.
          n_classes (int): The number of sleep stages for classification.
          hidden_size (int): The number of dimensions in the hidden state (Capacity of the memory of the model)
          num_layers (int): The number of GRU units.
          padding_value (int): The padding value used to fill the tensor to match the longest 
          sleep sequence in each batch during the training of the classifier.
        """
        super().__init__()
        self.name = name
  
        self.gru = nn.GRU(input_size=num_features, hidden_size=hidden_size,
                          batch_first=True, bidirectional=bidirectional, num_layers=num_layers)

        # Define the output layer that maps the hidden state to class logits.
        # If bidirectional, the hidden size is doubled as it concatenates the features from both directions.
        self.out = nn.Linear(in_features=hidden_size*2 if bidirectional else hidden_size, 
                             out_features=num_classes)

    def forward(self, x:torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
          x (Tensor): The input tensor containing features of shape (batch_size, rec_length, n_features).
          rec_lengths (Tensor): The actual lengths of each sleep sequence before padding.

        Returns:
          Tensor: The output logits of shape (batch_size, rec_length, n_classes).
        """
        # Pass the input through the GRU layer.   
        y_gru, _ = self.gru(x)
        
        # Pass the output of the GRU through the output layer to get class logits for each time step.
        y = self.out(y_gru)
        
        return y


class NappaAgePredict(NappaModel):  # Fixed the base class to be nn.Module directly
    def __init__(self, num_features=5, num_outputs=1, hidden_size=64, num_layers=1,
                 bidirectional=True):
        super().__init__()
        self.name = 'NappaAgePredict'
  
        self.gru = nn.GRU(input_size=num_features, hidden_size=hidden_size,
                          batch_first=True, bidirectional=bidirectional, num_layers=num_layers)

        # Define the output layer that maps the hidden state to class logits.
        # If bidirectional, the hidden size is doubled as it concatenates the features from both directions.
        self.out = nn.Linear(in_features=hidden_size * 2 if bidirectional else hidden_size, out_features=num_outputs)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through the network.
        
        Args:
          x (Tensor): The input tensor containing features of shape (batch_size, rec_length, num_features).

        Returns:
          Tensor: The output logits of shape (batch_size, num_outputs).
        """
        # Pass through the GRU
        y_gru, y_gru_final = self.gru(x)  # y_gru_final is of shape (num_layers * num_directions, batch_size, hidden_size)

        # Extract the final hidden state from the last layer
        if self.gru.bidirectional:
            # Concatenate the hidden states from the last forward and backward directions
            y_gru_final = torch.cat((y_gru_final[-2], y_gru_final[-1]), dim=1)  # For bidirectional GRU
        else:
            y_gru_final = y_gru_final[-1]  # Take the last layer hidden state for unidirectional GRU

        # Pass the final hidden state through the output layer
        y = self.out(y_gru_final)

        return y

        
class EnsembleClassifier:
    def __init__(self, model_class, weights_dir, model_args= {
                            'num_features'  :5,
                            'num_classes'   :3,
                            'hidden_size'   :10,
                            'num_layers'    :2,
                            'bidirectional' :True
                        }):
        """
        Initialize the general ensemble model. This can be used to construct an ensemble model
        from the cross validated NappaSleepNet models (weight files). This classifier produces
        predicted sleep classes by voting & averaging the model output distributions.

        Args:
          model (NappaSleepNet): Sleep classifier base class
          model_args (dict): Dictionary containing the initialization hyperparameters
          weights_dir (str): Directory where the pytorch model files (weights, .pth) are stored.
        """

        self.model_class = model_class
        self.model_args = model_args
        self.weights_dir = weights_dir
        self.i = 0
        # Load models in parallel
        self.models = self._load_models_in_parallel()


    def _load_single_model(self, weight_file):
        weight_file_path = os.path.join(self.weights_dir, weight_file)
        model = self.model_class(**self.model_args)  # Initialize new instance for each weight file
        model.load(weight_file_path)
        model.eval()
        return model

    def _load_models_in_parallel(self):
        weight_files = os.listdir(self.weights_dir)

        with ProcessPoolExecutor() as executor:
            models = list(executor.map(self._load_single_model, weight_files))

        return models

    def _predict_single_model(self, model, x):
        with torch.no_grad():
            preds = model.predict(x)[:, 0]  # First column contains the predicted sleep stages
            dists = model.predict(x)[:, 1:] # Rest columns contain the stage probabilities
            

        return preds, dists
    
    def predict(self, x, progress_callback=None, status_callback=None) -> torch.Tensor:
        """
        Predict the class for each time step using ensemble voting and classifier output averaging.

        Args:
          x (Tensor): The input tensor containing features of shape (rec_length, n_features).

        Returns:
          Tensor: The predicted classes and probability distributions of shape (rec_length, 1 + num_classes).
        """
        if status_callback:
            status_callback('Status: computing predictions...')
        # Parallelize predictions for all models using ProcessPoolExecutor
        with ProcessPoolExecutor() as executor:
            results = list(executor.map(self._predict_single_model, self.models, [x] * len(self.models)))

        all_predictions = []
        all_dists = []

        for i, (preds, dists) in enumerate(results):
            all_predictions.append(preds)
            all_dists.append(dists)

        # Stack the predictions to a tensor of shape (num_models, rec_length),
        # and transpose it to shape (rec_length, num_models) for majority voting.
        all_predictions = torch.transpose(torch.stack(all_predictions), 0, 1).type(torch.long)
        all_dists = torch.stack(all_dists)

        # Construct the predicted class vector by majority voting:
        voted_predictions = []
        for i in range(all_predictions.shape[0]):  # Iterate through each time step
            prediction = all_predictions[i]
            class_freq = torch.bincount(prediction)  # Count the frequency of each class
            most_popular_class = torch.argmax(class_freq)  # Get the most popular class
            voted_predictions.append(most_popular_class)

        voted_predictions = torch.tensor(voted_predictions)

        # Construct the predicted 'pseudo' distribution vector by averaging all the predictions
        mean_dists = torch.mean(all_dists, dim=0)

        # Scale the averaged distributions to add up to 1.
        normalized_mean_dists = torch.zeros((mean_dists.shape))
        for i in range(normalized_mean_dists.shape[0]):
            normalized_mean_dists[i] = mean_dists[i] / torch.sum(mean_dists[i])

        return torch.cat([voted_predictions.unsqueeze(-1), normalized_mean_dists], dim=1)