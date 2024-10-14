from funciones_traduccion import operar_boletines, claves_zonas
import os
import re

cod_periodo_boletin = 'FQXX41MM-2023' 
cod_boletin = re.match(r'[^-]+', cod_periodo_boletin).group() 
ruta_entrada = f'../../../datos/boletines/{cod_periodo_boletin}/bruto/'      
ruta_salida = f'../../../datos/boletines/{cod_periodo_boletin}/tratado/'
ruta_csv = f'../../../datasets/boletines/{cod_periodo_boletin}/'


nombre_boletin = "20230116_2000_FQXX41MM.txt"
arch_entrada = os.path.join(ruta_entrada, nombre_boletin)
arch_salida = "prueba.txt"

fenomeno = "ARRECIANDO BRUSCAMENTE A COMPONENTEW 7 O 8, 8 O 9 MAR ADENTRO, "


(seccion_boletin, dic_boletin, temp_boletin, boletin_sep_temp, dat_boletin, dat_final) = operar_boletines(arch_entrada, cod_boletin, ruta_csv)

with open(arch_salida, 'w', encoding='utf-8') as archivo_salida:
    archivo_salida.write(seccion_boletin)
    for i in range(1,5):
        archivo_salida.write(f"{claves_zonas(i, cod_boletin)}")
        archivo_salida.write(f"\n\n")
        for clave, valor in dic_boletin[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n\n")
        for clave, valor in temp_boletin[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n\n")
        for clave, valor in boletin_sep_temp[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n\n")
        for clave, valor in dat_boletin[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")
        archivo_salida.write(f"\n\n")
        for clave, valor in dat_final[i].items():
            archivo_salida.write(f"{clave}: {valor}\n")   
        archivo_salida.write(f"\n\n")

print("Proceso completado.")