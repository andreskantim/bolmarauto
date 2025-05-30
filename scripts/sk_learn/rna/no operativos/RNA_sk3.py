import sys
import os

import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, Normalizer
from sklearn.decomposition import PCA

from sklearn.neural_network import MLPRegressor

from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split

# Leer los datos de entrada y target
input = pd.read_csv("../../datasets/modelo/FQXX41MM2023/cantabria.csv")
target = pd.read_csv("../../datasets/boletines/FQXX41MM2023/cantabria.csv")
output_file = "../../predicciones/modelo/FQXX41MM2023/cantabria.csv"
copy_target = target.copy()
# Guardar las columnas 'emission_time' y 'valid_time' antes de eliminarlas
emission_time = target['emission_time']
valid_time = target['valid_time']

copy_target = target
input_columns = ['dwi', 'dwi_sin', 'dwi_cos', 'wind', 'shww', 'mdts', 'mdts_sin', 'mdts_cos', 'shts']
drop_input_columns = ['dwi', 'mdts']
columns_to_drop = []

# Identificar columnas para eliminar
for var in drop_input_columns:
    columns = [col for col in input.columns if pd.Series(col).str.contains(fr'{var}\([^\)]+\)', regex=True).any()]
    columns_to_drop += columns

input.drop(['emission_time', 'valid_time'], axis=1, inplace=True)
if columns_to_drop:
    input.drop(columns=columns_to_drop, axis=1, inplace=True)

target.drop(['emission_time', 'valid_time', 'dwi', 'mdts'], axis=1, inplace=True)

input = input.apply(lambda x: x.fillna(x.mean()), axis=0)
target = target.apply(lambda x: x.fillna(x.mean()), axis=0)

# Definir el Pipeline
pipe = Pipeline([
    ("imputer", SimpleImputer()),
    ("scaler", StandardScaler()),
    ("pca", PCA(n_components=0.99)),
    ("regressor", MLPRegressor(max_iter=2000, early_stopping=True))
])

# Definir parámetros para la búsqueda de hiperparámetros
grid_parametros = [
    {
        #"pca": [None, PCA(n_components=0.95)],
        "scaler": [None, StandardScaler()],
        "regressor__hidden_layer_sizes": [(30, 10)],
        "regressor__activation": ['relu', 'tanh', 'logistic'],
        "regressor__solver": ['adam'], # 'lbfgs' bueno con pocos datos, sino acaba estallando
        "regressor__learning_rate_init": [0.001, 0.01],
        "regressor__alpha": [0.0001, 0.001],   
        "regressor__batch_size": ['auto', 32]
        #"regressor__batch_size": ['auto', 16, 32, 64]
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

output_df = pd.DataFrame(index=copy_target.index)  

# Calcula el mejor modelo posible para cada variable meteorológica
for col in target.columns:  
    y = target[col]
    grid_search.fit(input, y)
    print(col)
    print(grid_parametros)
    print(grid_search.cv_results_['mean_test_score'])
    print(grid_search.cv_results_['std_test_score'])
    print(grid_search.cv_results_['rank_test_score'])

    # Obtener el mejor modelo
    best_model = grid_search.best_estimator_

    # Realizar predicciones con el mejor modelo
    predicciones = best_model.predict(input)
    output_df[col] = predicciones

# Añadir las columnas 'emission_time' y 'valid_time' al DataFrame de predicciones
output_df.insert(0, 'emission_time', emission_time)
output_df.insert(1, 'valid_time', valid_time)

# Guardar todas las predicciones en un solo archivo CSV
output_df.to_csv(output_file, index=False)




