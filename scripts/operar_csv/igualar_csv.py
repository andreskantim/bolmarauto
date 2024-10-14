import pandas as pd

# Rutas de los archivos CSV
archivo_csv1 = '../../datasets/modelo/FQXX41MM/cantabria.csv'
archivo_csv2 = '../../datasets/boletines/FQXX41MM/cantabria.csv'

# Cargar los archivos CSV en dataframes
df1 = pd.read_csv(archivo_csv1)
df2 = pd.read_csv(archivo_csv2)

# Verificar el número de filas en ambos dataframes
num_filas_df1 = len(df1)
num_filas_df2 = len(df2)

# Identificar las filas faltantes en df1
filas_faltantes_df1 = df2[~df2['emission_time'].isin(df1['emission_time'])]

# Identificar las filas faltantes en df2
filas_faltantes_df2 = df1[~df1['emission_time'].isin(df2['emission_time'])]

# Eliminar las filas adicionales de df1 y df2
if not filas_faltantes_df1.empty:
    df2 = df2[df2['emission_time'].isin(df1['emission_time'])]

if not filas_faltantes_df2.empty:
    df1 = df1[df1['emission_time'].isin(df2['emission_time'])]

# Verificar nuevamente el número de filas en ambos dataframes
num_filas_df1_final = len(df1)
num_filas_df2_final = len(df2)

if num_filas_df1_final == num_filas_df2_final:
    print("Ambos dataframes tienen el mismo número de filas después de la eliminación.")
    # Guardar los dataframes resultantes en los archivos originales
    df1.to_csv(archivo_csv1, index=False)
    df2.to_csv(archivo_csv2, index=False)
else:
    print("Los dataframes aún no tienen el mismo número de filas después de la eliminación.")
