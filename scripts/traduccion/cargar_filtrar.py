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

def cargar_archivos(nombre_archivo_txt):
    try:
        with open(nombre_archivo_txt, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
        
        # Buscar el inicio de la primera y la segunda sección
        I2 = contenido.find('%')
        I3 = contenido.find('&')
        
        if I2 == -1 or I3 == -1:
            raise ValueError("El documento no contiene los delimitadores esperados.")

        # Extraer las secciones y eliminar líneas vacías
        seccion1 = set(linea for linea in contenido[:I2].split('\n') if linea)
        seccion2 = set(linea for linea in contenido[I2+1:I3].split('\n') if linea)  # +1 para no incluir '%'
        seccion3 = set(linea for linea in contenido[I3+1:].split('\n') if linea)  # +1 para no incluir '&'

        return seccion1, seccion2, seccion3
    except FileNotFoundError:
        print(f"El archivo {nombre_archivo_txt} no se encontró.")
        return set(), set(), set()
    except ValueError as e:
        print(e)
        return set(), set(), set()
    
def separar_fenomenos(seccion,  neg_claves, claves):
    grupos = {i: [] for i in range(1, 6)}
    lineas = seccion['contenido'].split('\n')
    for grupo_id in range(1, 6):
        for linea in lineas:
            negado = False
            for neg_clave in neg_claves[grupo_id]:
                if re.findall(neg_clave, linea, re.IGNORECASE):
                    negado = True
                    break
            if negado:
                continue 
            
            coincide = False
            for clave in claves[grupo_id]:
                if re.findall(clave, linea, re.IGNORECASE):
                    coincide = True
                    break
            if coincide:
                grupos[grupo_id].append(linea)

    return grupos


def obtener_secciones(nombre_archivo, neg_claves, claves):
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

    secciones = {}
    matches = re.finditer(r'(AGUAS COSTERAS DE .*?)(?=AGUAS COSTERAS DE|\Z)', contenido, re.DOTALL)
    for i, match in enumerate(matches, start=1):
        secciones[i] = match.group(1)

    # Preparar el texto de salida
    texto_salida = fecha_hora_formateada + '\n\n'
    agrupado = {}

    for i, seccion in secciones.items():
        # Añadir salto de línea después de cada punto y eliminar espacio al principio de la línea siguiente
        seccion_modificada = re.sub(r'(\.)(?!\s*$)', r'\1\n', seccion)
        # Eliminar saltos de línea donde no hay punto final
        seccion_modificada = re.sub(r'(?<!\.)\n', '', seccion_modificada)
        # Eliminar espacios al principio de cada línea
        seccion_modificada = re.sub(r'^\s+', '', seccion_modificada, flags=re.MULTILINE)
        # Eliminar el nombre de la región en el encabezado de cada sección
        seccion_modificada = re.sub(r'^(.*?):', '', seccion_modificada)
        # Formatear la sección con el identificador de zona y contenido modificado
        zona_info = {'id': i, 'contenido': seccion_modificada.strip()}
        texto_salida += f"ZONA &{zona_info['id']}\n{zona_info['contenido']}\n\n"
        
        agrupado[i] = separar_fenomenos(zona_info, neg_claves, claves)

    return texto_salida.strip(), agrupado

