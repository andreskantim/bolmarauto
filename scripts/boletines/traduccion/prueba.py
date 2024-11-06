from funciones_traduccion import funcion_principal, parametros_zonas_y_divisiones
import os
import re

cod_periodo_boletin = 'FQXX41MM' 
cod_boletin = re.match(r'[^-]+', cod_periodo_boletin).group() 
ruta_entrada = f'../../../datos/boletines/{cod_periodo_boletin}/bruto/'      
ruta_salida = f'../../../datos/boletines/{cod_periodo_boletin}/tratado/'
ruta_csv = f'../../../datasets/boletines/{cod_periodo_boletin}/'


nombre_boletin = f"20140923_2000_{cod_periodo_boletin}.txt"
arch_entrada = os.path.join(ruta_entrada, nombre_boletin)
arch_salida = "prueba.txt"

num_zonas, num_divisiones, div_por_zona, dic_divisiones, zona_de_la_division, nombre_division, nombre_zona = parametros_zonas_y_divisiones(cod_boletin)

(seccion_boletin, dic_boletin, boletin_sep_fen, boletin_sep_zona, boletin_sep_temp, dat_boletin, dat_final) = funcion_principal(arch_entrada, cod_boletin, ruta_csv)

with open(arch_salida, 'w', encoding='utf-8') as archivo_salida:
    
    # for i in range(num_divisiones):
    for i in range(num_divisiones):
        
        archivo_salida.write(f"{nombre_zona[i]}")
        
        if nombre_division[i] != 0:
            archivo_salida.write(f"_{nombre_division[i]}" )
            
        archivo_salida.write(f"\n\n")
        archivo_salida.write(seccion_boletin[zona_de_la_division[i]])
        archivo_salida.write(f"\n")

        for clave, valor in dic_boletin[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n")

        for clave, valor in boletin_sep_fen[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n")

        for clave, valor in boletin_sep_zona[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n")

        for clave, valor in boletin_sep_temp[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n")

        for clave, valor in dat_boletin[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n")

        for clave, valor in dat_final[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")   
        archivo_salida.write(f"\n")

print("Proceso completado.")