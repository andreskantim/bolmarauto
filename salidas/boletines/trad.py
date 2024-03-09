import csv

# Función para cargar el diccionario desde un archivo
def cargar_diccionario(archivo_diccionario):
    diccionario = {}
    with open(archivo_diccionario, 'r') as f:
        for linea in f:
            (clave, valor) = linea.strip().split('=')
            diccionario[clave] = valor
    return diccionario

# Cargar el diccionario
diccionario = cargar_diccionario('diccionario.txt')

# Función para traducir el texto usando el diccionario
def traducir_texto(texto, diccionario):
    palabras = texto.split()
    return [diccionario.get(palabra, palabra) for palabra in palabras]

# Leer el archivo de texto
with open('datos.txt', 'r') as archivo_entrada:
    lineas = archivo_entrada.readlines()

# Preparar los datos para escribir en un archivo CSV
datos_para_csv = []
for linea in lineas:
    linea_traducida = traducir_texto(linea.strip(), diccionario)
    datos_para_csv.append(linea_traducida)

# Escribir los datos en un archivo CSV
with open('tabla_traducida.csv', 'w', newline='') as archivo_salida:
    escritor_csv = csv.writer(archivo_salida)
    escritor_csv.writerows(datos_para_csv)

print("La traducción ha sido completada y guardada en 'tabla_traducida.csv'.")