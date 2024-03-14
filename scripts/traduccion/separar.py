import regex as re

def leer_palabras_clave(doc):
    palabras_clave = {}
    for i in range(1, 6):
        # Inicializa un set vacío para cada categoría de palabras clave
        palabras_clave[i] = set()
        # Asegura que el archivo esté en el diccionario antes de intentar leerlo
        if i in doc:
            # Itera sobre cada línea del archivo
            for linea in doc[i]:
                palabra = linea.strip()
                if palabra == "%":
                    break  # Detiene la lectura al encontrar '%'
                else:
                    # Trata cualquier otra línea como una palabra clave literal
                    palabras_clave[i].add(palabra)
    return palabras_clave  # Distinguir entre palabras clave literales y patrones
                
def fenomenos_seccion(seccion, neg_claves, claves):
    grupos = {i: [] for i in range(1, 6)}
    # Dividir la sección en líneas
    lineas = seccion.split('\n')
    for linea in lineas:
        # Iterar sobre los grupos sin reordenarlos
        for grupo_id in range(1, 6):
            # Primero, verificar contra neg_claves
            negado = False
            for neg_clave in neg_claves[grupo_id]:
                if neg_clave.startswith('{') and neg_clave.endswith('}'):
                    patron = neg_clave[1:-1]
                    if re.search(patron, linea, re.IGNORECASE):
                        negado = True
                        break
                else:
                    if neg_clave in linea:
                        negado = True
                        break

            if negado:
                continue  # Si se encuentra una neg_clave, continuar con la siguiente línea sin añadir a grupos

            # Verificar ahora contra claves si la línea no fue negada
            coincide = False
            for clave in claves[grupo_id]:
                if clave.startswith('{') and clave.endswith('}'):
                    patron = clave[1:-1]
                    if re.search(patron, linea, re.IGNORECASE):
                        coincide = True
                        break
                else:
                    if clave in linea:
                        coincide = True
                        break

            if coincide:
                grupos[grupo_id].append(linea)
                break  # Si se encuentra una coincidencia, no es necesario seguir buscando en otros grupos

    return grupos

def prueba_tres_primeras_posiciones_con_cuatro_datos(diccionario):
    # Asegurarse de que las tres primeras posiciones tienen 4 elementos
    for i in range(1, 4):  # Itera sobre las posiciones 1, 2 y 3
        if len(diccionario[i]) != 4:
            return False
    return True