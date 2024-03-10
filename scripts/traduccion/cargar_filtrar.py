import re

def mes_a_numero(mes):
    meses = {
        "ENERO": "01",
        "FEBRERO": "02",
        "MARZO": "03",
        "ABRIL": "04",
        "MAYO": "05",
        "JUNIO": "06",
        "JULIO": "07",
        "AGOSTO": "08",
        "SEPTIEMBRE": "09",
        "OCTUBRE": "10",
        "NOVIEMBRE": "11",
        "DICIEMBRE": "12"
    }
    return meses.get(mes.upper(), "00")

def extraer_secciones_aguas_costeras_y_modificar(nombre_archivo):
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    # Extraer la fecha y hora de emisión del boletín
    fecha_hora_emision = re.search(r'EMITIDO A LAS (\d+:\d+) H.O. DEL (\w+) (\d+) DE (\w+) (\d+)', contenido)
    if fecha_hora_emision:
        # Convertir a formato YYYY/MM/DD HH:MM
        dia, mes, año = fecha_hora_emision.group(3), fecha_hora_emision.group(4), fecha_hora_emision.group(5)
        hora = fecha_hora_emision.group(1)
        mes_num=mes_a_numero(mes)
        # Asumiendo que ya tienes una forma de convertir el mes de texto a número, por ejemplo, "ENERO" a "01"
        # Este paso se omite aquí por simplicidad
        fecha_hora_formateada = f"{año}/{mes_num}/{dia} {hora}"

    # Excluir la tendencia de los avisos al final
    contenido = re.sub(r'TENDENCIA DE LOS AVISOS PARA LAS SIGUIENTES 24 HORAS\..*', '', contenido, flags=re.DOTALL)

    # Encontrar todas las secciones relevantes
    secciones = re.findall(r'(AGUAS COSTERAS DE .*?)(?=AGUAS COSTERAS DE|\Z)', contenido, re.DOTALL)

    # Preparar el texto de salida
    texto_salida = fecha_hora_formateada + '\n\n'  # Añadir la fecha y hora al inicio
    for i, seccion in enumerate(secciones, start=1):
        # Añadir salto de línea después de cada punto y eliminar espacio al principio de la línea siguiente
        seccion_modificada = re.sub(r'(\.)(?!\s*$)', r'\1\n', seccion)
        # Eliminar saltos de línea donde no hay punto final
        seccion_modificada = re.sub(r'(?<!\.)\n', '', seccion_modificada)
        # Eliminar espacios al principio de cada línea
        seccion_modificada = re.sub(r'^\s+', '', seccion_modificada, flags=re.MULTILINE)
        # Eliminar el nombre de la región en el encabezado de cada sección
        seccion_modificada = re.sub(r'^(.*?):', '', seccion_modificada)
        # Formatear la sección con el identificador de zona y contenido modificado
        zona_info = f'ZONA &{i}\n{seccion_modificada.strip()}'
        texto_salida += zona_info + '\n\n'

    return texto_salida.strip()