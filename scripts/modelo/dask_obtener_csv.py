import xarray as xr
import pandas as pd
import numpy as np
import os
import dask

from dask.diagnostics import ProgressBar
import dask.dataframe as dd

codigo_boletin = 'FQXX41MM'
zona_boletin = 'cantabria'
año = '2023'
ruta_entrada = f'../../datos/antiguos_modelo/{codigo_boletin}/{zona_boletin}'      
ruta_salida = f'../../datasets/modelo/{codigo_boletin}{año}'

if not os.path.isdir(ruta_salida):
    os.makedirs(ruta_salida)

# Leer todos los archivos GRIB con Dask + xarray
archivos_grib = [
    os.path.join(ruta_entrada, f) 
    for f in os.listdir(ruta_entrada)
    if (f.endswith('.grib') or f.endswith('.grib2')) and 
       (not año or f.startswith(año))  # Filtra si 'año' está definido, de lo contrario no aplica el filtro
]

datasets = [xr.open_dataset(f, engine='cfgrib', decode_timedelta=False, chunks={}) for f in archivos_grib]

# Concatenar con Dask por la dimensión "time"
datos_combinados = xr.concat(datasets, dim='time')

# Convertimos a DataFrame de forma diferida
df = datos_combinados.to_dask_dataframe()

# Reset index y manipulaciones básicas
df = df.reset_index()
df['time'] = dd.to_datetime(df['time'])

df['step_num'] = (df['step'] - 12) / 3 + 1
df['step_num'] = df['step_num'].astype(int)

# Calculamos los validate_time
df['valid_time'] = df['time'] + df['step']

# Filtramos por rangos
df_mañana = df[(df['step_num'] >= 1) & (df['step_num'] <= 9)]
df_tarde = df[(df['step_num'] >= 3) & (df['step_num'] <= 11)]

# Asignamos hora de emisión
df_mañana['emission_time'] = df_mañana['time'].dt.floor('D') + pd.Timedelta(hours=12)
df_tarde['emission_time'] = df_tarde['time'].dt.floor('D') + pd.Timedelta(hours=18)

df = dd.concat([df_mañana, df_tarde])

# Calcular senos y cosenos
df['dwi_sin'] = np.sin(np.radians(df['dwi']))
df['dwi_cos'] = np.cos(np.radians(df['dwi']))
df['mdts_sin'] = np.sin(np.radians(df['mdts']))
df['mdts_cos'] = np.cos(np.radians(df['mdts']))

# Eliminamos columnas innecesarias
df = df.drop(columns=['number', 'heightAboveGround', 'meanSea', 'step', 'time', 'step_num'])

# Reordenamos columnas
cols = ['dwi', 'dwi_sin', 'dwi_cos', 'wind', 'shww', 'mdts', 'mdts_sin', 'mdts_cos', 'shts',
        'emission_time', 'valid_time', 'latitude', 'longitude']
df = df[cols]

# Convertimos a pandas para agrupamiento final (Dask no permite fácilmente custom apply con `iterrows`)
with ProgressBar():
    df = df.compute()

# AGRUPACIÓN FINAL — igual que en tu código original
def concat_row_values(group):
    concatenated_values = {}
    for _, row in group.iterrows():
        for col in ['dwi', 'dwi_sin', 'dwi_cos', 'wind', 'shww', 'mdts', 'mdts_sin', 'mdts_cos', 'shts']:
            column_name = f'{col}({row["longitude"]},{row["latitude"]})'
            concatenated_values[column_name] = row[col]
    return pd.Series(concatenated_values)

df.reset_index(drop=True, inplace=True)
result = df.groupby(['emission_time', 'valid_time'], as_index=False).apply(concat_row_values, include_groups=False)

result.set_index(['emission_time', 'valid_time'], inplace=True)

archivo_salida = f'{ruta_salida}/{zona_boletin}.csv'
result.to_csv(archivo_salida)



# ####################################### POR VARIABLES #############################################

# variables = ['dwi', 'dwi_sin', 'dwi_cos', 'wind', 'shww', 'mdts', 'mdts_sin', 'mdts_cos', 'shts']

# def concat_row_values(group, var):
#     concatenated_values = {}
#     for _, row in group.iterrows():
#         column_name = f'{var}({row["longitude"]},{row["latitude"]})'
#         concatenated_values[column_name] = row[var]
#     return pd.Series(concatenated_values)

# for var in variables:
#     # Aplicamos la función para cada variable, incluyendo include_groups=False
#     result2 = df.groupby(['emission_time', 'valid_time'], as_index=False).apply(concat_row_values, var, include_groups=False)
    
#     # Reestructuramos el DataFrame resultante si es necesario
#     result2 = result2.reset_index(drop=True)
#     # Aquí, asumimos que 'final_combined_time' ya está incluido correctamente. Si no, ajusta según sea necesario.
    
#     # Guardamos el resultado en un archivo CSV
#     archivo_salida = f'{ruta_salida}{var}.csv'
#     result2.to_csv(archivo_salida, index=False)

# ##################################################################################



