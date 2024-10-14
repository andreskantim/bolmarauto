import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.metrics import mean_squared_error
from rich import print

# Definición de la clase MLPRegressor para PyTorch
class MLPRegressor(nn.Module):
    def __init__(self, number_inputs, hidden_layers=[10]):
        super(MLPRegressor, self).__init__()
        layers = []
        input_size = number_inputs
        for hidden_size in hidden_layers:
            layers.append(nn.Linear(input_size, hidden_size))
            layers.append(nn.ReLU())
            input_size = hidden_size
        layers.append(nn.Linear(input_size, 1))
        self.layers = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.layers(x)

# Funciones para entrenar y evaluar el modelo
def train_model(model, dataset, optimizer, criterion, epochs=100, batch_size=32, device='cpu'):
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    model.train()
    model.to(device)
    for epoch in range(epochs):
        for data, targets in dataloader:
            data, targets = data.to(device), targets.to(device)
            optimizer.zero_grad()
            outputs = model(data).squeeze()
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
        if (epoch + 1) % 10 == 0:
            print(f'Epoch {epoch+1}, Loss: {loss.item()}')

def evaluate_model(model, dataset, criterion, batch_size=32, device='cpu'):
    dataloader = DataLoader(dataset, batch_size=batch_size)
    model.eval()
    model.to(device)
    total_loss = 0.0
    total_samples = 0

    with torch.no_grad():
        for data, targets in dataloader:
            data, targets = data.to(device), targets.to(device)
            outputs = model(data).squeeze()
            loss = criterion(outputs, targets)
            total_loss += loss.item() * data.size(0)
            total_samples += data.size(0)

    avg_loss = total_loss / total_samples
    print(f'Evaluation Loss: {avg_loss}')
    return avg_loss

# Clase PytornWrapper para integrarse con scikit-learn
class PytornWrapper:
    def __init__(self, hidden_layers=[10], lr=0.001, epochs=100, batch_size=32, device='cpu'):
        self.hidden_layers = hidden_layers
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = device
        self.model = None
        self.criterion = nn.MSELoss()
        self.optimizer = None
        self.number_inputs = None

    def set_params(self, **params):
        for param, value in params.items():
            setattr(self, param, value)
        if self.number_inputs:
            self.model = MLPRegressor(self.number_inputs, self.hidden_layers).to(self.device)
            self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        return self

    def fit(self, X, y):
        self.number_inputs = X.shape[1]
        self.model = MLPRegressor(self.number_inputs, self.hidden_layers).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)

        X_torch = torch.tensor(X, dtype=torch.float32).to(self.device)
        y_torch = torch.tensor(y, dtype=torch.float32).to(self.device)
        dataset = TensorDataset(X_torch, y_torch)
        train_model(self.model, dataset, self.optimizer, self.criterion, self.epochs, self.batch_size, self.device)
    
    def predict(self, X):
        X_torch = torch.tensor(X, dtype=torch.float32).to(self.device)
        self.model.eval()
        with torch.no_grad():
            return self.model(X_torch).cpu().numpy()
    
    def score(self, X, y):
        X_torch = torch.tensor(X, dtype=torch.float32).to(self.device)
        y_torch = torch.tensor(y, dtype=torch.float32).to(self.device)
        return -evaluate_model(self.model, TensorDataset(X_torch, y_torch), self.criterion, self.batch_size, self.device)
