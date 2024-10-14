from funciones_prediccion import (
    vaciar_directorio,
    operar_prediccion
)
import pandas as pd
import numpy as np
import os
import re

cod_periodo_boletin = 'FQXX41MM-2023' 
cod_boletin = re.match(r'[^-]+', cod_periodo_boletin).group()
zona = 'cantabria.csv'
archivo_entrada = f'../../predicciones/modelo/{cod_periodo_boletin}/cantabria.csv'      
ruta_salida = f'../../predicciones/boletines/{cod_periodo_boletin}/bruto/'
ruta_final = f'../../predicciones/boletines/{cod_periodo_boletin}/tratado/'
ruta_claves = "claves/"

vaciar_directorio(ruta_salida)
vaciar_directorio(ruta_final)

df = pd.read_csv(os.path.join(archivo_entrada))
    
for i in range(0, len(df), 9): 

    boletin_csv = df.iloc[i:i+9]
    
    if len(boletin_csv) < 9:
        boletin_csv = boletin_csv.reindex(range(i, i+9))

    boletin_csv.reset_index(drop=True, inplace=True)

    tabla_boletin, texto_boletin, texto_prueba, dia, hora_emision, dbg = operar_prediccion(boletin_csv)

    nombre_boletin = f"{dia}_{hora_emision}_{cod_boletin}_cantabria.txt"

    arch_salida = os.path.join(ruta_salida, nombre_boletin)
    arch_final = os.path.join(ruta_final, nombre_boletin)

    with open(arch_salida, 'w') as archivo_salida:
        archivo_salida.write(tabla_boletin)
        archivo_salida.write("\n\n")
        archivo_salida.write(texto_prueba)
        archivo_salida.write("\n\n")
        archivo_salida.write(texto_boletin)
        archivo_salida.write("\n\n")
        archivo_salida.write(dbg)

    with open(arch_final, 'w') as archivo_final:
        archivo_final.write(texto_boletin)
    
    
print("Proceso completado.")