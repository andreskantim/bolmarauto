import os
import re
import subprocess

# Lista de boletines donde se encuentran los archivos tratados
boletines = ["FQXX40MM", "FQXX41MM", "FQXX42MM", "FQXX43MM"] 
# boletines = ["FQXX41MM"]  # Añadir más boletines según sea necesario

# Expresión que quieres buscar
expresion_buscar = r"(?:AL FINAL|AL PRINCIPIO|MAS TARDE|EN TODAS? LAS? ZONAS?|EN AMBAS ZONAS|EN EL RESTO|EN EL RESTO)\s?(?:DE LA|DEL)?\s?(?:TARDE|MANANA|DIA|MADRUGADA|MEDIODIA|NOCHE)?\s?(?:AREAS DE|INTERVALOS DE)?\s?(?:FUERTE\s?MA(?:RE{1,2})?JADA|MA(?:RE{1,2})?JADILLA|RIZADA|MA(?:RE{1,2})?JADA|MUY\s?GRUESA|GRUESA|ARBOLADA|MONTANOSA|ENORME)"
# expresion_buscar = r"HACIA EL NORTE "

# Lista para almacenar los archivos encontrados que contienen la expresión
archivos_encontrados = []

# Archivo para guardar los resultados de la búsqueda
archivo_resultados = 'buscar.txt'

# Recorrer cada boletín en la lista
with open(archivo_resultados, mode='w', encoding='utf-8') as buscar_file:
    for boletin in boletines:
        carpeta_tratado = f'../../datos/boletines/{boletin}/tratado/'
        
        # Comprobar si la carpeta existe antes de intentar listar los archivos
        if not os.path.exists(carpeta_tratado):
            buscar_file.write(f"Error: La carpeta no existe - {carpeta_tratado}\n")
            continue  # Pasar al siguiente boletín si la carpeta no existe

        # Recorrer todos los archivos de la carpeta "tratado"
        for nombre_archivo in sorted(os.listdir(carpeta_tratado)):
            # Asegurarse de que solo se procesen archivos de texto
            if nombre_archivo.endswith('.txt'):
                archivo_completo = os.path.join(carpeta_tratado, nombre_archivo)

                try:
                    # Abrir y leer el archivo línea por línea
                    with open(archivo_completo, 'r', encoding='utf-8') as file:
                        for numero_linea, linea in enumerate(file, start=1):
                            # Buscar la expresión dentro de la línea
                            match = re.search(expresion_buscar, linea)
                            if match:
                                # Si se encuentra la expresión, agregar el archivo y la línea a la lista
                                archivos_encontrados.append(nombre_archivo)
                                # Capturar la expresión encontrada
                                expresion_capturada = match.group()
                                # Obtener las posiciones de inicio y fin
                                inicio, fin = match.span()
                                # Escribir el nombre del archivo, la línea, la expresión capturada y las posiciones en el archivo de resultados
                                buscar_file.write(
                                    f"Archivo: {nombre_archivo} - Posiciones: (Inicio: {inicio}, Fin: {fin}) - "
                                    f"Línea {numero_linea}: {linea.strip()}\n"
                                )

                                break  # Si ya lo encuentra, no busca más en el archivo actual

                except FileNotFoundError:
                    buscar_file.write(f"Error: Archivo no encontrado - {nombre_archivo}\n")
                except Exception as e:
                    buscar_file.write(f"Error inesperado en archivo {nombre_archivo}: {e}\n")

# Abrir los primeros 5 archivos encontrados en VSCode
# for nombre_archivo in archivos_encontrados[:5]:
#     archivo_para_abrir = os.path.join(carpeta_tratado, nombre_archivo)
    
#     if os.path.exists(archivo_para_abrir):
#         subprocess.run(['code', archivo_para_abrir])  # Abrir el archivo en VSCode
#     else:
#         with open(archivo_resultados, mode='a', encoding='utf-8') as buscar_file:
#             buscar_file.write(f"Error: El archivo {archivo_para_abrir} no se encontró.\n")

