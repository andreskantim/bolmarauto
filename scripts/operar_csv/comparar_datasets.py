import xarray as xr
import os
import pandas as pd
import numpy as np

# Ruta de entrada donde se encuentra el archivo con datos del viento
ruta_entrada_antiguo = "../../datos/antiguos_modelo/FQXX41MM/guipuzcua/"
ruta_entrada= "../../datos/antiguos_modelo/FQXX41MM/guipuzcua/"

# Archivos a procesar
archivo_antiguo = '202001.grib'  # Archivo con módulo y ángulo
archivo_atm = 'guipuzcua_202001_atm.grib' # Archivo con 10u y 10v
archivo_wave = 'guipuzcua_202001_wave.grib'  

# Cargar el archivo GRIB que contiene el viento en módulo y ángulo
ruta_archivo_wind = os.path.join(ruta_entrada_antiguo, archivo_antiguo)
ds_wind = xr.open_dataset(ruta_archivo_wind, engine='cfgrib')

# Convertimos el dataset a DataFrame
df_wind = ds_wind.to_dataframe()
df_wind.reset_index(inplace=True)
df_wind['time'] = pd.to_datetime(df_wind['time'])

# Convertir 'step' a un valor entero de 1 a 11
df_wind['step_num'] = df_wind['step'].apply(lambda x: ((x.total_seconds() // 3600) - 12) / 3 + 1)
df_wind['step_num'] = df_wind['step_num'].astype(int)

# Calculamos los 'valid_time'
df_wind['valid_time'] = df_wind['time'] + pd.to_timedelta(df_wind['step'], unit='h')

# Duplicar los datos para cubrir emisiones a las 12 y 18 horas
df_mañana = df_wind.copy()
df_tarde = df_wind.copy()

df_mañana = df_mañana[(df_mañana['step_num'] >= 1) & (df_mañana['step_num'] <= 9)]
df_tarde = df_tarde[(df_tarde['step_num'] >= 3) & (df_tarde['step_num'] <= 11)]

df_mañana['emission_time'] = df_mañana['time'].dt.floor('D') + pd.Timedelta(hours=12)
df_tarde['emission_time'] = df_tarde['time'].dt.floor('D') + pd.Timedelta(hours=18)

# Concatenamos los DataFrames de mañana y tarde
df_wind = pd.concat([df_mañana, df_tarde])

# Establecer nuevo índice en df_wind
df_wind.set_index(['emission_time', 'valid_time', 'latitude', 'longitude'], inplace=True)

# Cargar el archivo GRIB que contiene los componentes U y V
ruta_archivo_uv = os.path.join(ruta_entrada, archivo_atm)
ds_uv = xr.open_dataset(ruta_archivo_uv, engine='cfgrib')

# Convertir el segundo archivo a DataFrame
df_uv = ds_uv.to_dataframe()
df_uv.reset_index(inplace=True)
df_uv['time'] = pd.to_datetime(df_uv['time'])

# Calcular valid_time y otros campos en df_uv
df_uv['step_num'] = df_uv['step'].apply(lambda x: ((x.total_seconds() // 3600) - 12) / 3 + 1)
df_uv['step_num'] = df_uv['step_num'].astype(int)
df_uv['valid_time'] = df_uv['time'] + pd.to_timedelta(df_uv['step'], unit='h')

# Seleccionar los mismos periodos de emisión para df_uv
df_uv_mañana = df_uv.copy()
df_uv_tarde = df_uv.copy()
df_uv_mañana['emission_time'] = df_uv_mañana['time'].dt.floor('D') + pd.Timedelta(hours=12)
df_uv_tarde['emission_time'] = df_uv_tarde['time'].dt.floor('D') + pd.Timedelta(hours=18)

# Concatenamos las versiones de la mañana y la tarde de df_uv
df_uv = pd.concat([df_uv_mañana, df_uv_tarde])

# Establecer el mismo índice en df_uv
df_uv.set_index(['emission_time', 'valid_time', 'latitude', 'longitude'], inplace=True)

# Unimos los dos DataFrames por el índice
df_combinado = df_wind.join(df_uv, lsuffix='_atm', rsuffix='', how='inner')

# Calcular la diferencia entre los componentes U y V
# Suponiendo que los nombres de las columnas son '10u' y '10v' para el archivo de componentes U y V

# Convierte de grados a radianes para la conversión a componentes
df_combinado['dwi'] = np.deg2rad(df_combinado['dwi'])  # Cambia 'wind_angle' por el nombre real

# Calcula las componentes U y V
df_combinado['u_wind'] = -1 * df_combinado['wind'] * np.sin(df_combinado['dwi'])
df_combinado['v_wind'] = -1 * df_combinado['wind'] * np.cos(df_combinado['dwi'])

df_combinado['Diff_U'] = df_combinado['u10'] - df_combinado['u_wind']  # Cambia 'wind_u' por el nombre real del componente u del viento en módulo
df_combinado['Diff_V'] = df_combinado['v10'] - df_combinado['v_wind']  # Cambia 'wind_v' por el nombre real del componente v del viento en módulo

ruta_archivo_wave = os.path.join(ruta_entrada, archivo_wave)
ds_wave = xr.open_dataset(ruta_archivo_wave, engine='cfgrib')

# Convertir el segundo archivo a DataFrame
ds_wave = ds_wave.to_dataframe()
ds_wave.reset_index(inplace=True)
ds_wave['time'] = pd.to_datetime(ds_wave['time'])

# Calcular valid_time y otros campos en df_uv
ds_wave['step_num'] = ds_wave['step'].apply(lambda x: ((x.total_seconds() // 3600) - 12) / 3 + 1)
ds_wave['step_num'] = ds_wave['step_num'].astype(int)
ds_wave['valid_time'] = ds_wave['time'] + pd.to_timedelta(ds_wave['step'], unit='h')

# Seleccionar los mismos periodos de emisión para df_uv
ds_wave_mañana = ds_wave.copy()
ds_wave_tarde = ds_wave.copy()
ds_wave_mañana['emission_time'] = ds_wave_mañana['time'].dt.floor('D') + pd.Timedelta(hours=12)
ds_wave_tarde['emission_time'] = ds_wave_tarde['time'].dt.floor('D') + pd.Timedelta(hours=18)

# Concatenamos las versiones de la mañana y la tarde de df_uv
ds_wave = pd.concat([ds_wave_mañana, ds_wave_tarde])

# Establecer el mismo índice en df_uv
ds_wave.set_index(['emission_time', 'valid_time', 'latitude', 'longitude'], inplace=True)

ds_wave = ds_wave.rename({'shww': 'shww_wave', 'mdts': 'mdts_wave', 'shts': 'shts_wave'})

# Unimos los dos DataFrames por el índice
df_combinado = df_combinado.join(ds_wave, lsuffix='_wave', rsuffix='', how='inner')

print(df_combinado)

df_combinado['Diff_shww'] = df_combinado['shww'] - df_combinado['shww_wave']  
df_combinado['Diff_mdts'] = df_combinado['mdts'] - df_combinado['mdts_wave']
df_combinado['Diff_shts'] = df_combinado['shts'] - df_combinado['shts_wave']

# Seleccionar las columnas de interés
# resultado_final = df_combinado[['u10', 'u_wind', 'Diff_U', 'v10',  'v_wind', 'Diff_V']] 
resultado_final = df_combinado[['Diff_U', 'Diff_V', 'Diff_shww', 'Diff_mdts', 'Diff_shts']] 

# Exportar a CSV
resultado_final.to_csv('comparar_datasets.csv')
print("Diferencias guardadas en 'comparar_datasets.csv'.")