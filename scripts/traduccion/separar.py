def leer_palabras_clave(nombre_archivo):
    palabras_clave = set()
    with open(nombre_archivo, 'r') as archivo:
        for linea in archivo:
            palabra = linea.strip()
            if palabra == "%":
                break  # Detiene la lectura al encontrar '%'
            # Distinguir entre palabras clave literales y patrones
            if palabra.startswith('{') and palabra.endswith('}'):
                # Extrae el contenido dentro de las llaves y lo trata como un patrón regex
                patron = palabra[1:-1]
                palabras_clave.add(patron)
            else:
                palabras_clave.add(palabra)
    return palabras_clave

palabras_viento = leer_palabras_clave('viento.txt')
palabras_mar_viento = leer_palabras_clave('mar_viento.txt')
palabras_mar_fondo = leer_palabras_clave('mar_fondo.txt')
palabras_meteoros = leer_palabras_clave('meteoros.txt')
palabras_visibilidad = leer_palabras_clave('visibilidad.txt')

# Este es el texto de ejemplo que quieres clasificar
texto = """
Esto es un ejemplo con palabra1 que debería ir al primer grupo.
Esta frase contiene palabra4 y va al segundo grupo.
Aquí tenemos palabra3 así que pertenece al primer grupo.
Finalmente, esta frase tiene palabra6 y corresponde al segundo grupo.
"""

# Separa el texto en frases o porciones
frases = texto.split('\n')  # Aquí usamos el salto de línea como delimitador

# Listas para almacenar las frases clasificadas
grupo_1 = []
grupo_2 = []

# Función para determinar a qué grupo pertenece una frase
def clasificar_frase(frase, grupo_1, grupo_2):
    palabras = set(frase.split())
    if palabras_clave_grupo_1.intersection(palabras):
        grupo_1.append(frase)
    elif palabras_clave_grupo_2.intersection(palabras):
        grupo_2.append(frase)

# Procesa cada frase
for frase in frases:
    clasificar_frase(frase, grupo_1, grupo_2)

# Imprime los resultados
print("Grupo 1:")
for frase in grupo_1:
    print(frase)

print("\nGrupo 2:")
for frase in grupo_2:
    print(frase)