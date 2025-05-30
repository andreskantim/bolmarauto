import torch
import pandas as pd
import numpy as np
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.base import BaseEstimator, RegressorMixin

# Clase MLPRegressor para PyTorch
class MLPRegressor(nn.Module):
    def __init__(self, number_inputs, hidden_layers=[10], activation=nn.ReLU):# 👈 nuevo
        super(MLPRegressor, self).__init__()
        layers = []
        input_size = number_inputs
        for hidden_size in hidden_layers:
            layers.append(nn.Linear(input_size, hidden_size))
            layers.append(activation())   # 👈 nuevo
            input_size = hidden_size
        layers.append(nn.Linear(input_size, 1))
        self.layers = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.layers(x)

# Funciones para entrenar y evaluar el modelo
def train_model(model, dataset, optimizer, criterion, epochs=100, batch_size=32):
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model.train()
   
    for epoch in range(epochs):
        for data, targets in dataloader:
            optimizer.zero_grad()
            outputs = model(data).squeeze()
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

def evaluate_model(model, dataset, criterion, batch_size=32):
    dataloader = DataLoader(dataset, batch_size=batch_size)
    model.eval()
    total_loss = 0.0
    total_samples = 0

    with torch.no_grad():
        for data, targets in dataloader:
            outputs = model(data).squeeze()
            loss = criterion(outputs, targets)
            total_loss += loss.item() * data.size(0)
            total_samples += data.size(0)

    avg_loss = total_loss / total_samples
    print(f'Evaluation Loss: {avg_loss}')
    return avg_loss

# Clase PytorchWrapper para integrarse con scikit-learn
class PytorchWrapper(BaseEstimator, RegressorMixin):
    def __init__(self, hidden_layers=[10], activation=nn.ReLU, lr=0.001, epochs=100, batch_size=32):
        self.hidden_layers = hidden_layers
        self.activation = activation  # 👈 nuevo
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None
        self.criterion = nn.MSELoss()
        self.optimizer = None
        self.number_inputs = None

    def set_params(self, **params):
        for param, value in params.items():
            setattr(self, param, value)
        if self.number_inputs:
            self.model = MLPRegressor(self.number_inputs, self.hidden_layers, self.activation) # 👈 nuevo
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        return self

    def fit(self, X, y):
        self.number_inputs = X.shape[1]
        
        X_torch = torch.tensor(X.values if isinstance(X, pd.DataFrame) else X, dtype=torch.float32)
        y_torch = torch.tensor(y.values if isinstance(y, pd.Series) else y, dtype=torch.float32)  
        
        self.model = MLPRegressor(self.number_inputs, self.hidden_layers, self.activation) # 👈 nuevo
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        
        dataset = TensorDataset(X_torch, y_torch)
        train_model(self.model, dataset, self.optimizer, self.criterion, self.epochs, self.batch_size)
    
    def predict(self, X):
        X_torch = torch.tensor(X.values if isinstance(X, pd.DataFrame) else X, dtype=torch.float32)
        self.model.eval()
        with torch.no_grad():
            return self.model(X_torch).cpu().numpy()

    def score(self, X, y):
        X_torch = torch.tensor(X.values if isinstance(X, pd.DataFrame) else X, dtype=torch.float32)
        y_torch = torch.tensor(y.values if isinstance(y, pd.Series) else y, dtype=torch.float32)  
        return -evaluate_model(self.model, TensorDataset(X_torch, y_torch), self.criterion, self.batch_size)
