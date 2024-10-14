import xarray as xr
import pandas as pd
from pandas.tseries.offsets import Hour
from datetime import datetime
import os

zona_boletin = 'cantabria'
fecha_boletin = '2023'
ruta_entrada = f'../datos/modelo/{zona_boletin}/{fecha_boletin}/'      
ruta_salida = f'../datasets/modelo/{zona_boletin}/{fecha_boletin}/'
archivo_salida = ruta_salida + f'{fecha_boletin}.csv'

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

exclusion = pd.to_timedelta('1 days 12 hours')
filtro = df['step'] != exclusion
df = df[filtro]

df['date'] = df['time'] + df['step']

df = df[['date', 'latitude', 'longitude', 'dwi', 'wind', 'shww', 'mdts', 'shts']]

df.sort_values(by=['date', 'latitude', 'longitude'], inplace=True)

df.set_index(['date', 'latitude', 'longitude'], inplace=True) #Aqui tenemos el formato principal
 
df.to_csv(archivo_salida)

####################################################################################

df.reset_index(inplace=True)

def concat_row_values(group):
    concatenated_values = {}
    # Iteramos por cada fila en el grupo para construir los nombres de columna
    for _, row in group.iterrows():
        for col in ['dwi', 'wind', 'shww', 'mdts', 'shts']:
            # Construimos el nombre de la columna como 'nombre_columna(longitud,latitud)'
            column_name = f'{col}({row["longitude"]},{row["latitude"]})'
            concatenated_values[column_name] = row[col]
    return pd.Series(concatenated_values)

# Agrupamos por 'final_combined_time' y aplicamos la función
result = df.groupby('date', as_index=False).apply(concat_row_values, include_groups=False)

result.set_index(['date'], inplace=True)

archivo_salida = f'{ruta_salida}grouped-{fecha_boletin}.csv'
result.to_csv(archivo_salida)

####################################################################################

variables = ['dwi', 'wind', 'shww', 'mdts', 'shts']

def concat_row_values(group, var):
    concatenated_values = {}
    for _, row in group.iterrows():
        column_name = f'{var}({row["longitude"]},{row["latitude"]})'
        concatenated_values[column_name] = row[var]
    return pd.Series(concatenated_values)

for var in variables:
    # Aplicamos la función para cada variable, incluyendo include_groups=False
    result2 = df.groupby('date', as_index=False).apply(concat_row_values, var, include_groups=False)
    
    # Reestructuramos el DataFrame resultante si es necesario
    result2 = result2.reset_index(drop=True)
    # Aquí, asumimos que 'final_combined_time' ya está incluido correctamente. Si no, ajusta según sea necesario.
    
    # Guardamos el resultado en un archivo CSV
    archivo_salida = f'{ruta_salida}{var}-{fecha_boletin}.csv'
    result2.to_csv(archivo_salida, index=False)

##################################################################################
