import xarray as xr
import pandas as pd
import numpy as np
import os

codigo_boletin = 'FQXX41MM'
zona_boletin = 'asturias'
ruta_entrada = f'../../datos/modelo/{codigo_boletin}/{zona_boletin}'      
ruta_salida = f'../../datasets/modelo/{codigo_boletin}'

if not os.path.isdir(ruta_salida):
    os.makedirs(ruta_salida)


datasets = []

# Itera sobre los archivos en el directorio de entrada
for archivo in os.listdir(ruta_entrada):
    if archivo.endswith('.grib') or archivo.endswith('.grib2'):
        # Construye la ruta completa del archivo
        ruta_archivo = os.path.join(ruta_entrada, archivo)
        
        # Abre el archivo GRIB usando xarray y cfgrib como backend
        ds = xr.open_dataset(ruta_archivo, engine='cfgrib')
        
        # Agrega el dataset a la lista
        datasets.append(ds)

datos_combinados = xr.concat(datasets, dim='time')

# Opcionalmente, puedes realizar alguna transformación o selección de datos aquí

df = datos_combinados.to_dataframe()

df.reset_index(inplace=True)
df['time'] = pd.to_datetime(df['time'])

# Convertir 'step' a un valor entero de 1 a 11
df['step_num'] = df['step'].apply(lambda x: ((x.total_seconds() // 3600) - 12) / 3 + 1)
df['step_num'] = df['step_num'].astype(int)

# Calculamos los validate_time
df['valid_time'] = df['time'] + pd.to_timedelta(df['step'], unit='h')

# Duplicar los datos para cubrir emisiones a las 12 y 18 horas
df_mañana = df.copy()
df_tarde = df.copy()

df_mañana = df_mañana[(df_mañana['step_num'] >= 1) & (df_mañana['step_num'] <= 9)]
df_tarde = df_tarde[(df_tarde['step_num'] >= 3) & (df_tarde['step_num'] <= 11)]

df_mañana['emission_time'] = df_mañana['time'].dt.floor('D') + pd.Timedelta(hours=12)
df_tarde['emission_time'] = df_tarde['time'].dt.floor('D') + pd.Timedelta(hours=18)

# Concatenamos el DataFrame modificado con el duplicado
df = pd.concat([df_mañana, df_tarde])



# Establecer nuevo índice
df.set_index(['emission_time', 'valid_time', 'latitude', 'longitude'], inplace=True)

# Ordenar el DataFrame por los nuevos índices   
df.sort_index(inplace=True)

df['dwi_sin'] = np.sin(np.radians(df['dwi']))
df['dwi_cos'] = np.cos(np.radians(df['dwi']))
df['mdts_sin'] = np.sin(np.radians(df['mdts']))
df['mdts_cos'] = np.cos(np.radians(df['mdts']))

df.drop(columns=['number', 'heightAboveGround', 'meanSea', 'step', 'time', 'step_num'], inplace=True)

df = df[['dwi', 'dwi_sin', 'dwi_cos', 'wind', 'shww', 'mdts', 'mdts_sin', 'mdts_cos', 'shts']]

# archivo_salida = f'{ruta_salida}{zona_boletin}_completo.csv'
# df.to_csv(archivo_salida)

# ######################################## AGRUPANDO LATITUD Y LONGUITUD ############################################

df.reset_index(inplace=True)

def concat_row_values(group):
    concatenated_values = {}
    # Iteramos por cada fila en el grupo para construir los nombres de columna
    for _, row in group.iterrows():
        for col in ['dwi', 'dwi_sin', 'dwi_cos', 'wind', 'shww', 'mdts', 'mdts_sin', 'mdts_cos', 'shts']:
            # Construimos el nombre de la columna como 'nombre_columna(longitud,latitud)'
            column_name = f'{col}({row["longitude"]},{row["latitude"]})'
            concatenated_values[column_name] = row[col]
    return pd.Series(concatenated_values)

# Agrupamos por 'final_combined_time' y aplicamos la función
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



