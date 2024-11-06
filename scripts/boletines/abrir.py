import os
import subprocess

# Carpeta donde se encuentran los archivos boletines
boletin = "FQXX41MM"
carpeta_tratado = f'../../datos/boletines/{boletin}/tratado/'

# Solicitar al usuario que introduzca las fechas, separadas por saltos de línea
fechas_input = """
2014-09-26 12:00:00
2015-07-19 12:00:00
2015-08-18 18:00:00
2016-04-10 12:00:00
2016-05-01 18:00:00
2016-05-30 12:00:00
2017-04-17 18:00:00
2017-08-07 18:00:00
2017-12-30 12:00:00
2017-12-30 18:00:00
2018-10-30 12:00:00
2018-12-15 12:00:00
2018-12-15 12:00:00
2018-12-15 12:00:00
2018-12-15 12:00:00
2019-01-25 12:00:00
2019-06-07 12:00:00
2020-05-10 12:00:00
2020-05-10 12:00:00
2020-05-10 12:00:00
2020-05-10 18:00:00
2020-05-10 18:00:00
2020-09-26 18:00:00
2020-09-26 18:00:00
2020-09-26 18:00:00
2020-12-07 12:00:00
2020-12-07 18:00:00
2021-01-17 12:00:00
2021-09-23 18:00:00
2022-01-09 12:00:00
2022-01-09 18:00:00
2022-02-27 12:00:00
2022-05-13 12:00:00
2022-05-13 18:00:00
2022-06-11 18:00:00
2022-06-11 18:00:00
2022-08-20 12:00:00
2022-10-23 12:00:00
2022-10-23 12:00:00
2022-10-23 12:00:00
2022-10-23 12:00:00
2022-10-23 12:00:00
2022-10-23 12:00:00
2022-10-23 12:00:00
2022-10-23 18:00:00
2022-10-23 18:00:00
2022-10-23 18:00:00
2022-10-23 18:00:00
2023-02-08 12:00:00
2023-02-26 18:00:00
2024-03-27 12:00:00
"""

# Dividir la entrada en una lista de fechas
fechas = fechas_input.strip().split("\n")  # Eliminar espacios en blanco y dividir por líneas

# Función para generar el nombre del archivo a partir de la fecha
def generar_nombre_archivo(fecha):
    partes = fecha.split()  # Divide por espacio en [fecha, hora]
    fecha_formato = partes[0].replace("-", "")  # Quita los guiones para formar YYYYMMDD
    hora = partes[1][:2]  # Obtiene las primeras dos cifras de la hora (HH)
    
    # Determina si el sufijo es '_12' o '_20'
    if hora == "12":
        sufijo = "_12"
    elif hora == "18":
        sufijo = "_20"
    else:
        return None  # Si no es ni 12 ni 18, retorna None

    return f"{fecha_formato}{sufijo}00_{boletin}.txt"  # Retorna el nombre completo del archivo

# Recorrer las fechas y abrir los archivos correspondientes
for fecha in fechas:
    nombre_archivo = generar_nombre_archivo(fecha)
    if nombre_archivo:
        archivo_completo = os.path.join(carpeta_tratado, nombre_archivo)
        
        if os.path.exists(archivo_completo):
            subprocess.run(['code', archivo_completo])  # Abre el archivo en VSCode
        else:
            print(f"El archivo {archivo_completo} no se encontró.")
    else:
        print(f"Fecha no válida o fuera del rango esperado: {fecha}")
