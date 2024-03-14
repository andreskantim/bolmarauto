from cargar_filtrar import extraer_secciones_aguas_costeras_y_modificar, extraer_secciones_del_documento
from separar import leer_palabras_clave, fenomenos_seccion, prueba_tres_primeras_posiciones_con_cuatro_datos
import os

neg_claves={}
claves={}
traduccion={}

(neg_claves[1],claves[1],traduccion[1]) = extraer_secciones_del_documento("viento.txt")
(neg_claves[2],claves[2],traduccion[2]) = extraer_secciones_del_documento("mar_viento.txt")
(neg_claves[3],claves[3],traduccion[3]) = extraer_secciones_del_documento("mar_fondo.txt")
(neg_claves[4],claves[4],traduccion[4]) = extraer_secciones_del_documento("meteoros.txt")
(neg_claves[5],claves[5],traduccion[5]) = extraer_secciones_del_documento("visibilidad.txt")

def escribir_archivo(informacion, arch_salida):
    with open(arch_salida, 'w', encoding='utf-8') as archivo_salida:
        archivo_salida.write(informacion)

def escribir_diccionario(informacion, arch_salida):
    with open(arch_salida, 'w', encoding='utf-8') as archivo_salida:
        for clave, valor in informacion.items():
            archivo_salida.write(f"{clave}: {valor}\n")

#palabras_clave = leer_palabras_clave(doc)  # Asegúrate de que 'doc' esté correctamente definido o sustitúyelo por la fuente correcta de palabras clave

ruta_entrada = '/home/andreskantim/ecmwf/datos/boletines/FQXX41MM/'      
ruta_salida = '/home/andreskantim/ecmwf/datos/boletines/pruebas/'   

archivos = [f for f in os.listdir(ruta_entrada) if os.path.isfile(os.path.join(ruta_entrada, f))]
archivos.sort() 
# Procesar cada archivo

archivo_resultados_prueba = os.path.join(ruta_salida, "resultados_prueba.txt")
with open(archivo_resultados_prueba, 'w', encoding='utf-8') as archivo_resultados:
    # Procesar cada archivo
    for nombre_archivo in archivos:
        arch_entrada = os.path.join(ruta_entrada, nombre_archivo)
        arch_salida = os.path.join(ruta_salida, nombre_archivo + "_B")
        arch_prueba = os.path.join(ruta_salida, nombre_archivo + "_F")

        # Procesar el archivo de entrada
        seccion_boletin = extraer_secciones_aguas_costeras_y_modificar(arch_entrada)

        # Escribir la información modificada en el archivo de salida
        escribir_archivo(seccion_boletin, arch_salida)

        agrupado = fenomenos_seccion(seccion_boletin, neg_claves, claves)

        condicion_prueba = prueba_tres_primeras_posiciones_con_cuatro_datos(agrupado)

        # Escribir resultado de prueba
        archivo_resultados.write(f"{nombre_archivo}: {condicion_prueba}\n")

        #print(f"La información ha sido procesada y escrita en {arch_salida}. La prueba de las tres primeras posiciones con cuatro datos resultó en {condicion_prueba} para {nombre_archivo}.")

print("Proceso completado.")