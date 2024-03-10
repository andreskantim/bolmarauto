import re

def mes_a_numero(mes):
    # Esta función debe convertir el nombre del mes a número
    pass  # Implementa según sea necesario

def extraer_secciones_aguas_costeras_y_modificar(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    # Extraer la fecha y hora de emisión del boletín
    fecha_hora_emision = re.search(r'EMITIDO A LAS (\d+:\d+) H.O. DEL (\w+) (\d+) DE (\w+) (\d+)', contenido)
    if fecha_hora_emision:
        # Convertir a formato YYYY/MM/DD HH:MM
        dia, mes, año = fecha_hora_emision.group(3), fecha_hora_emision.group(4), fecha_hora_emision.group(5)
        hora = fecha_hora_emision.group(1)
        mes_num = mes_a_numero(mes)
        fecha_hora_formateada = f"{año}/{mes_num}/{dia} {hora}"

    # Excluir la tendencia de los avisos al final
    contenido = re.sub(r'TENDENCIA DE LOS AVISOS PARA LAS SIGUIENTES 24 HORAS\..*', '', contenido, flags=re.DOTALL)

    # Encontrar todas las secciones relevantes
    secciones = re.findall(r'AGUAS COSTERAS DE (.*?)(?=AGUAS COSTERAS DE|\Z)', contenido, re.DOTALL)

    texto_salida = fecha_hora_formateada + '\n\n'
    for i, seccion in enumerate(secciones, start=1):
        # Aquí es donde identificamos y organizamos las partes
        partes = []
        for j in range(1, 6):  # Asumiendo 5 partes como máximo
            parte = re.search(f'PARTE{j}:(.*?)(?=PARTE{j+1}:|\Z)', seccion, re.DOTALL)
            if parte:
                partes.append(parte.group(1).strip())

        # Unir las partes separadas por dos saltos de línea, después de procesarlas
        seccion_modificada = '\n\n'.join(partes)
        # Añadir el identificador de zona y contenido modificado
        zona_info = f'ZONA &{i}\n{seccion_modificada}'
        texto_salida += zona_info + '\n\n'

    return texto_salida.strip()

def escribir_informacion_en_archivo(informacion, nombre_archivo_salida):
    with open(nombre_archivo_salida, 'w', encoding='utf-8') as archivo_salida:
        archivo_salida.write(informacion)

# Ruta al archivo de entrada
nombre_archivo_entrada = '/home/andreskantim/ecmwf/datos/boletines/FQXX41MM/20150101_1200_FQXX41MM.txt'

# Ruta al archivo de salida
nombre_archivo_salida = '/home/andreskantim/ecmwf/datos/boletines/FQXX41MM/T_20150101_1200_FQXX41MM.txt'

# Procesar el archivo de entrada
informacion_modificada = extraer_secciones_aguas_costeras_y_modificar(nombre_archivo_entrada)

# Escribir la información modificada en el archivo de salida
escribir_informacion_en_archivo(informacion_modificada, nombre_archivo_salida)

print(f"La información ha sido escrita en {nombre_archivo_salida}.")