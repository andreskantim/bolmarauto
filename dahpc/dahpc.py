import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import Hour
from datetime import datetime
import os

zona_boletin = 'cantabria'
fecha_boletin = '2023'    
ruta_entrada = f'../datasets/modelo/{zona_boletin}/{fecha_boletin}/'
archivo_entrada = ruta_entrada + f'{fecha_boletin}.csv'

df=pd.read_csv(archivo_entrada, index_col=[ 'date', 'latitude', 'longitude'])

# print(df)

# print(df.describe())
def med_ang(var_angular):

    df['cos'] = np.cos(np.radians(var_angular))
    df['sin'] = np.sin(np.radians(var_angular))

    # Calcular la media de los componentes
    mean_cos = df['cos'].mean()
    mean_sin = df['sin'].mean()

    df.drop(columns=['sin', 'cos'], inplace=True)

    # Convertir las medias de los componentes de vuelta a un ángulo
    mean_direction = np.degrees(np.arctan2(mean_sin, mean_cos))
    # Normalizar el resultado para que esté en el rango [0, 360)
    mean_direction = mean_direction % 360
    
    return mean_direction

med_dwi=med_ang(df['dwi'])

############################1. Cálculo de media latitudinal y longitudinal y visualización####################################


df.reset_index(inplace=True)
df.set_index(['longitude', 'latitude'], inplace=True)
df['date'] = pd.to_datetime(df['date'])
df_day=df['dwi'].groupby(df['date'].dt.dayofyear).max()
df_month=df[['dwi','wind']].groupby(df['date'].dt.month).max()
print(df_month)

#########################################################################################################################




# # Ploteo
# variables = ['dwi', 'wind', 'shww', 'mdts', 'shts']
# for var in variables:
#     plt.figure(figsize=(10,6))
#     media_movil_7d[var].plot(title=f'Media móvil de 7 días para {var}')
#     plt.ylabel(var)
#     plt.xlabel('Fecha')
#     plt.show()

# # Para shts y shww con distinto eje
# fig, ax1 = plt.subplots(figsize=(12, 6))

# color = 'tab:green'
# ax1.set_xlabel('Fecha')
# ax1.set_ylabel('shts', color=color)
# ax1.plot(media_movil_7d.index, media_movil_7d['shts'], color=color, label='shts (media móvil 7 días)')
# ax1.tick_params(axis='y', labelcolor=color)

# # Instancia un segundo eje que comparte el mismo eje x
# ax2 = ax1.twinx()
# color = 'tab:blue'
# ax2.set_ylabel('shww', color=color)
# ax2.plot(media_movil_7d.index, media_movil_7d['shww'], color=color, label='shww (media móvil 7 días)')
# ax2.tick_params(axis='y', labelcolor=color)

# # Añade las leyendas
# lines, labels = ax1.get_legend_handles_labels()
# lines2, labels2 = ax2.get_legend_handles_labels()
# ax2.legend(lines + lines2, labels + labels2, loc='upper left')

# # Título del gráfico
# plt.title('Comparación de shts y shww (Media móvil de 7 días)')

# plt.show()

###########################2. Máximo, mínimo horario, promedio diario y mensual############################################

# # Máximo, mínimo horario
# max_hourly = df.resample('H').max()
# min_hourly = df.resample('H').min()

# # Promedio diario
# avg_daily = df.resample('D').mean()

# # Promedio mensual
# avg_monthly = df.resample('M').mean()

# ###################################3. Promedio longitudinal para latitudes específicas###################################

# lat_43_46 = df.xs(43.46, level='latitude')
# lat_43_83 = df.xs(43.83, level='latitude')

# # Ahora puedes agrupar por fecha y calcular el promedio para cada DataFrame filtrado.
# avg_43_46 = lat_43_46.groupby(lat_43_46.index.get_level_values('date')).mean()
# avg_43_83 = lat_43_83.groupby(lat_43_83.index.get_level_values('date')).mean()

# ###########################4. Promedio temporal total#############################################

# total_avg = df.mean()

# # Para identificar el punto con el valor máximo/mínimo, puedes usar:
# max_point = total_avg.idxmax()
# min_point = total_avg.idxmin()

# ############################5. Histograma para dwi y mdts#############################################

# bins = [0, 22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5, 360]
# labels = ['Norte', 'Noreste', 'Este', 'Sureste', 'Sur', 'Suroeste', 'Oeste', 'Noroeste', 'Norte']
# df['dwi_dir'] = pd.cut(df['dwi'], bins=bins, labels=labels, right=False)
# df['mdts_dir'] = pd.cut(df['mdts'], bins=bins, labels=labels, right=False)

# # Ahora, puedes hacer un histograma para cada una
# df['dwi_dir'].value_counts().plot(kind='bar')
# plt.show()

# df['mdts_dir'].value_counts().plot(kind='bar')
# plt.show()

# ####################################6. Buscar correlaciones####################################

# # Calcula el promedio como se necesite, aquí un ejemplo general
# avg_values = df.mean()

# # Correlación
# correlation_matrix = avg_values.corr()

# # Para ver la correlación específica entre pares
# print(correlation_matrix.loc[['wind', 'shts', 'shww'], ['dwi', 'mdts']])