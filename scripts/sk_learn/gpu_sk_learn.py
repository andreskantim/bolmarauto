import pandas as pd
import torch
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from rich import print

from gpu_funciones_pytorch import PytornWrapper

input = pd.read_csv("/home/ulc/cursos/curso342/ecmwf/datasets/modelo/FQXX41MM-2023/cantabria.csv")
target = pd.read_csv("/home/ulc/cursos/curso342/ecmwf/datasets/boletines/FQXX41MM-2023/cantabria.csv")

input_columns = ['dwi', 'dwi_sin', 'dwi_cos', 'wind', 'shww', 'mdts', 'mdts_sin', 'mdts_cos', 'shts']
drop_input_columns = ['dwi', 'mdts']
columns_to_drop = [] 

for var in drop_input_columns:
    columns = [col for col in input.columns if pd.Series(col).str.contains(fr'{var}\([^\)]+\)', regex=True).any()]
    columns_to_drop += columns  

input.drop(['emission_time', 'valid_time'], axis=1, inplace=True)
if columns_to_drop:
    input.drop(columns=columns_to_drop, axis=1, inplace=True)

target.drop(['emission_time', 'valid_time', 'dwi', 'mdts'], axis=1, inplace=True)

input = input.apply(lambda x: x.fillna(x.mean()), axis=0)
target = target.apply(lambda x: x.fillna(x.mean()), axis=0)

target = target.wind_max

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando el dispositivo: {device}")

X = torch.tensor(input.values, dtype=torch.float32).to(device)
y = torch.tensor(target.values, dtype=torch.float32).to(device)

# Definir el Pipeline
pipe = Pipeline([
    ("imputer", SimpleImputer()),
    ("scaler", StandardScaler()),
    ("pca", PCA(n_components=0.99)),
    ("regressor", PytornWrapper(device=device))
])

# Definir parámetros para la búsqueda de hiperparámetros
grid_parametros = [
    {
        "regressor": [PytornWrapper()],
        # 'pca': [None, PCA(n_components=0.99)], 
        # 'scaler': [StandardScaler(), Normalizer()],
        'regressor__hidden_layers': [(5,), (10,), (15,), (25,), (35,), (50,)],
        # 'regressor__lr': [0.01, 0.05],
        'regressor__epochs': [30],
        # 'regressor__batch_size': [16, 32]
    }
    ,
    {
        'regressor': [MLPRegressor(max_iter=500, early_stopping=True)], 
        'regressor__hidden_layer_sizes': [(100,50), (100,), (10,), (30,10)]
    }
    ,
    {
        'regressor': [SVR()], 
        'pca': [None, PCA(n_components=0.95)]
    }
]

# Realizar la búsqueda de hiperparámetros
grid_search = GridSearchCV(
    pipe, 
    grid_parametros, 
    cv=10,
    scoring='neg_root_mean_squared_error',
    return_train_score=True,
    n_jobs=-1
)

grid_search.fit(X.cpu().numpy(), y.cpu().numpy())

# Imprimir resultados
print(grid_search.cv_results_['mean_test_score'])
print(grid_search.cv_results_['std_test_score'])
print(grid_search.cv_results_['rank_test_score'])
