import sys
import math
import pandas as pd
import os

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, Normalizer, RobustScaler, MinMaxScaler 
from sklearn.decomposition import PCA

from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsRegressor

from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import train_test_split

from rich import print

# Leer los datos de entrada y target
input = pd.read_csv("../../datasets/modelo/FQXX41MM/cantabria.csv")
target = pd.read_csv("../../datasets/boletines/FQXX41MM/cantabria.csv")
output_file = "../../predicciones/modelo/FQXX41MM/cantabria_RF.csv"
best_results_csv = "../../scripts/sk_learn/TFM2/resultados/RF_resultados.csv"

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

# Función para interpolación de valores faltantes
def interpolate_missing_values(df):
    """
    Interpola valores NaN y 'None' usando los 2 valores no nulos más cercanos.
    Para secuencias largas de valores faltantes, usa interpolación sin límite
    y luego aplica fallback con la media si es necesario.
    
    EXCEPCIÓN: Para variables dwi_sin, dwi_cos, mdts_sin, mdts_cos
    se sustituye directamente por la media sin interpolación.
    """
    df_copy = df.copy()
    
    # Reemplazar 'None' por NaN
    df_copy = df_copy.replace('None', pd.NA)
    
    # Variables especiales que se rellenan solo con la media
    special_vars = ['dwi_sin', 'dwi_cos', 'mdts_sin', 'mdts_cos']
    
    # Aplicar interpolación por columna
    for col in df_copy.columns:
        # Convertir a numérico si es posible
        df_copy[col] = pd.to_numeric(df_copy[col], errors='coerce')
        
        if col in special_vars:
            # Para variables especiales: solo usar la media
            print(f"Aplicando media para variable especial: {col}")
            df_copy[col] = df_copy[col].fillna(df_copy[col].mean())
        else:
            # Para el resto: interpolación normal
            # Primero intentar interpolación sin límite
            df_copy[col] = df_copy[col].interpolate(method='linear', limit_direction='both')
            
            # Si aún quedan valores NaN (por ejemplo, al inicio o final de la serie),
            # usar forward fill y backward fill
            df_copy[col] = df_copy[col].ffill().bfill()
            
            # Como último recurso, si todavía hay NaN, usar la media
            if df_copy[col].isna().any():
                df_copy[col] = df_copy[col].fillna(df_copy[col].mean())
    
    return df_copy

# Aplicar interpolación en lugar de rellenar con la media
input = interpolate_missing_values(input)
target = interpolate_missing_values(target)


# Definir el Pipeline
pipe = Pipeline([
    ("imputer", SimpleImputer()),
    ("scaler", StandardScaler()),
    ("pca", None),
    ("regressor", SVR())
])

# Definir parámetros para la búsqueda de hiperparámetros
grid_parametros = [
    {
    'regressor': [RandomForestRegressor()],
    'regressor__n_estimators': [200, 400],
    'regressor__max_depth': [20],
    'regressor__min_samples_split': [2, 6, 10],
    'regressor__min_samples_leaf': [4, 8, 12],
    'regressor__max_features': ['log2']
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

# Lista para almacenar todos los resultados
all_results = []

# Calcula el mejor modelo posible para cada variable meteorológica
for col in target.columns:  
    y = target[col]
    grid_search.fit(input, y)
    
    # Imprimir en consola
    print(f"Variable: {col}")
    print(f"Mejor score: {grid_search.best_score_}")
    print(f"Mejores parámetros: {grid_search.best_params_}")
    print(grid_parametros)
    print(grid_search.cv_results_['mean_test_score'])
    print(grid_search.cv_results_['std_test_score'])
    print(grid_search.cv_results_['rank_test_score'])
    print("-" * 50)

    # Obtener el mejor modelo
    best_model = grid_search.best_estimator_

    # Realizar predicciones con el mejor modelo
    predicciones = best_model.predict(input)
    output_df[col] = predicciones
    
    # Almacenar resultados para escritura posterior
    best_params = grid_search.best_params_
    result_data = {
        'variable': col,
        'best_score': grid_search.best_score_,
        'best_params': grid_search.best_params_,
        'mean_test_score': grid_search.cv_results_['mean_test_score'],
        'std_test_score': grid_search.cv_results_['std_test_score'],
        'rank_test_score': grid_search.cv_results_['rank_test_score'],
        'csv_row': {
            'variable': col,
            'regressor': 'RandomForestRegressor',
            'n_estimators': best_params['regressor__n_estimators'],
            'max_depth': best_params['regressor__max_depth'],
            'min_samples_split': best_params['regressor__min_samples_split'],
            'min_samples_leaf': best_params['regressor__min_samples_leaf'],
            'max_features': best_params['regressor__max_features'],
            'best_score': grid_search.best_score_
        }
    }
    all_results.append(result_data)

# Escribir archivo CSV con todos los resultados
try:
    csv_data = [result['csv_row'] for result in all_results]
    results_df = pd.DataFrame(csv_data)
    results_df.to_csv(best_results_csv, index=False)
    print(f"✓ Archivo CSV de resultados guardado: {best_results_csv}")
    
except Exception as e:
    print(f"✗ Error al guardar CSV de resultados: {e}")

# Añadir las columnas 'emission_time' y 'valid_time' al DataFrame de predicciones
output_df.insert(0, 'emission_time', emission_time)
output_df.insert(1, 'valid_time', valid_time)

# Guardar todas las predicciones en un solo archivo CSV
output_df.to_csv(output_file, index=False)

print(f"\nArchivos guardados:")
print(f"- Predicciones: {output_file}")
print(f"- Mejores resultados: {best_results_csv}")