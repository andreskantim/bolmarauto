from cargar_filtrar import cargar_archivos, obtener_secciones
import os

neg_claves={}
claves={}
traduccion={}

(neg_claves[1],claves[1],traduccion[1]) = cargar_archivos("viento.txt")
(neg_claves[2],claves[2],traduccion[2]) = cargar_archivos("mar_viento.txt")
(neg_claves[3],claves[3],traduccion[3]) = cargar_archivos("mar_fondo.txt")
(neg_claves[4],claves[4],traduccion[4]) = cargar_archivos("meteoros.txt")
(neg_claves[5],claves[5],traduccion[5]) = cargar_archivos("visibilidad.txt")

def escribir_archivo(informacion, arch_salida):
    with open(arch_salida, 'w', encoding='utf-8') as archivo_salida:
        archivo_salida.write(informacion)

def escribir_diccionario(informacion, arch_salida):
    with open(arch_salida, 'w', encoding='utf-8') as archivo_salida:
        for clave, valor in informacion.items():
            archivo_salida.write(f"{clave}: {valor}\n")

ruta_entrada = '/home/andreskantim/ecmwf/datos/boletines/FQXX41MM/'      
ruta_salida = '/home/andreskantim/ecmwf/datos/boletines/pruebas/'   

archivos = [f for f in os.listdir(ruta_entrada) if os.path.isfile(os.path.join(ruta_entrada, f))]
archivos.sort() 
# Procesar cada archivo

archivo_resultados_prueba = os.path.join(ruta_salida, "resultados_prueba.txt")
with open(archivo_resultados_prueba, 'w', encoding='utf-8') as archivo_resultados:
    for nombre_archivo in archivos:
        arch_entrada = os.path.join(ruta_entrada, nombre_archivo)
        arch_salida = os.path.join(ruta_salida, nombre_archivo + "_B")
        arch_prueba = os.path.join(ruta_salida, nombre_archivo + "_F")

        (seccion_boletin, agrupado) = obtener_secciones(arch_entrada, neg_claves, claves)

        escribir_archivo(seccion_boletin, arch_salida)

        escribir_diccionario(agrupado, arch_prueba)
        
print("Proceso completado.")