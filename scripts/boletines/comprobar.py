import csv
import os
import subprocess  # Para abrir los archivos en VSCode

# Carpeta que contiene los archivos CSV
boletin = "FQXX41MM"
carpeta_csv = f'../../datasets/boletines/{boletin}/'  # Cambia esto a la ruta de tu carpeta
carpeta_tratado = f'../../datos/boletines/{boletin}/tratado/'  # Carpeta donde se encuentran los archivos para abrir en VSCode

# Lista de archivos CSV en la carpeta
archivos_csv = sorted([f for f in os.listdir(carpeta_csv) if f.endswith('.csv')])

# Lista para almacenar los nombres únicos de archivos que necesitan abrirse en el orden en que se encuentran
archivos_a_abrir = []

# Abrir el archivo errores.txt para escritura
with open('comprobar.txt', mode='w') as errores_file:
    # Iterar sobre cada archivo CSV
    for nombre_archivo in archivos_csv:
        archivo_csv = os.path.join(carpeta_csv, nombre_archivo)  # Ruta completa del archivo
        lineas_sin_valor = []

        try:
            # Leer el archivo CSV
            with open(archivo_csv, mode='r', newline='') as csvfile:
                lector = csv.reader(csvfile)
                encabezados = next(lector)  # Lee la primera fila (encabezados)

                # Verificar que las columnas existen antes de obtener sus índices
                columnas_requeridas = ['wind_max', 'wind_med', 'shww_max', 'shww_med']
                if not all(col in encabezados for col in columnas_requeridas):
                    raise ValueError(f"El archivo {nombre_archivo} no contiene todas las columnas necesarias.")

                # Encontrar los índices de las columnas que nos interesan
                indice_wind_max = encabezados.index('wind_max')
                indice_wind_med = encabezados.index('wind_med')
                indice_shww_max = encabezados.index('shww_max')
                indice_shww_med = encabezados.index('shww_med')

                # Obtener el índice de la primera columna (la que tiene la fecha y hora)
                indice_fecha_hora = 0

                # Iterar sobre las filas restantes
                for numero_fila, fila in enumerate(lector, start=2):  # Comienza en 2 para incluir encabezados
                    
                    condicion1 = (fila[indice_wind_max].strip() == '' or fila[indice_wind_max] == 'None' or
                        fila[indice_wind_med].strip() == '' or fila[indice_wind_med] == 'None' or
                        fila[indice_shww_max].strip() == '' or fila[indice_shww_max] == 'None' or
                        fila[indice_shww_med].strip() == '' or fila[indice_shww_med] == 'None')
                    
                    # Verificar si las columnas están vacías o tienen el valor 'None' o espacios vacíos
                    if (condicion1):
                        
                        # Extraer la fecha y hora de la primera columna
                        fecha_hora = fila[indice_fecha_hora]
                        # Formato esperado: 'YYYY-MM-DD HH:MM:SS'
                        if "12:00:00" in fecha_hora:
                            nombre_archivo_tratado = fecha_hora[:10].replace("-", "") + "_12"
                        elif "18:00:00" in fecha_hora:
                            nombre_archivo_tratado = fecha_hora[:10].replace("-", "") + "_20"
                        else:
                            continue  # Si no coincide con los tiempos esperados, omitir

                        # Agregar el nombre del archivo tratado a la lista (solo si no está repetido)
                        if nombre_archivo_tratado not in archivos_a_abrir:
                            archivos_a_abrir.append(nombre_archivo_tratado)

                        # Agregar la línea y el número de fila a la lista de errores
                        lineas_sin_valor.append((numero_fila, fila))

            # Escribir resultados en errores.txt
            if lineas_sin_valor:
                errores_file.write(f"\nArchivo: {nombre_archivo}\n")
                for numero_fila, linea in lineas_sin_valor:
                    errores_file.write(f"Línea {numero_fila}: {','.join(linea)}\n")  # Escribir el número de línea y la línea
            else:
                errores_file.write(f"\nArchivo: {nombre_archivo} - No se encontraron líneas sin valores.\n")

        except FileNotFoundError:
            errores_file.write(f"Error: Archivo no encontrado - {nombre_archivo}\n")
        except ValueError as ve:
            errores_file.write(f"Error: {ve}\n")
        except Exception as e:
            errores_file.write(f"Error inesperado al procesar el archivo {nombre_archivo}: {e}\n")

# Abrir los primeros 5 archivos únicos en VSCode en el orden en que se encontraron

for nombre_archivo_tratado in archivos_a_abrir[:5]:
    print(nombre_archivo_tratado)

    archivo_para_abrir = os.path.join(carpeta_tratado, nombre_archivo_tratado + f'00_{boletin}.txt')  # Suponiendo que los archivos son .txt
    if os.path.exists(archivo_para_abrir):
        subprocess.run(['code', archivo_para_abrir])  # Abre el archivo en VSCode
    else:
        with open('errores.txt', mode='a') as errores_file:
            errores_file.write(f"Error: El archivo tratado {archivo_para_abrir} no se encontró.\n")

