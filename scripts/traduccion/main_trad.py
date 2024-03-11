from cargar_filtrar import extraer_secciones_aguas_costeras_y_modificar
from separar import leer_palabras_clave
#buscar libreria parsear 
doc_viento = open("viento.txt", 'r')
doc_mar_viento = open("mar_viento.txt", 'r')
doc_mar_fondo = open("mar_fondo.txt", 'r')
doc_meteoros = open("meteoros.txt", 'r')
doc_visibilidad = open("visibilidad.txt", 'r')

def escribir_informacion_en_archivo(informacion, arch_salida):
    with open(arch_salida, 'w', encoding='utf-8') as archivo_salida:
        archivo_salida.write(informacion)

# Ruta al archivo de entrada
arch_entrada = '/home/andreskantim/ecmwf/datos/boletines/FQXX41MM/20150101_1200_FQXX41MM.txt'

# Ruta al archivo de salida
arch_salida = '/home/andreskantim/ecmwf/datos/boletines/FQXX41MM/T_20150101_1200_FQXX41MM.txt'

# Procesar el archivo de entrada
informacion_modificada = extraer_secciones_aguas_costeras_y_modificar(arch_entrada)

# Escribir la información modificada en el archivo de salida
escribir_informacion_en_archivo(informacion_modificada, arch_salida)

doc_viento.close()
doc_mar_viento.close()
doc_mar_fondo.close()
doc_meteoros.close()
doc_visibilidad.close()

print(f"La información ha sido escrita en {arch_salida}.")