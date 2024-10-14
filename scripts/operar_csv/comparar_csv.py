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

# Comparar los números de filas
if num_filas_df1 != num_filas_df2:
    # Identificar las filas faltantes en df1
    filas_faltantes_df1 = df2[~df2['emission_time'].isin(df1['emission_time'])]

    # Identificar las filas faltantes en df2
    filas_faltantes_df2 = df1[~df1['emission_time'].isin(df2['emission_time'])]

    # Imprimir o guardar las filas faltantes en nuevos archivos CSV si es necesario
    if not filas_faltantes_df1.empty:
        print("Filas faltantes en df1:")
        print(filas_faltantes_df1)
        # Si deseas guardar las filas faltantes en un archivo CSV
        filas_faltantes_df1.to_csv('filas_faltantes_df1.csv', index=False)

    if not filas_faltantes_df2.empty:
        print("Filas faltantes en df2:")
        print(filas_faltantes_df2)
        # Si deseas guardar las filas faltantes en un archivo CSV
        filas_faltantes_df2.to_csv('filas_faltantes_df2.csv', index=False)
else:
    print("Ambos dataframes tienen el mismo número de filas.")