import re
import csv
import os
import pandas as pd
import numpy as np
import shutil

def vaciar_directorio(directorio):
    
    shutil.rmtree(directorio, ignore_errors=True)
    
    os.makedirs(directorio, exist_ok=True)

def reconstruir_angulo(seno, coseno):

    # magnitud = np.sqrt(seno ** 2 + coseno ** 2)
    # seno = seno / magnitud
    # coseno = coseno / magnitud

    angulo = np.arctan2(seno, coseno)
    angulo = np.degrees(angulo)
    
    angulo = np.where(angulo < 0, angulo + 360, angulo)

    return angulo

def clasificar_angulo(angulo):
    if (angulo >= 337.5) or (angulo < 22.5):
        return 0
    elif 22.5 <= angulo < 67.5:
        return 1
    elif 67.5 <= angulo < 112.5:
        return 2
    elif 112.5 <= angulo < 157.5:
        return 3
    elif 157.5 <= angulo < 202.5:
        return 4
    elif 202.5 <= angulo < 247.5:
        return 5
    elif 247.5 <= angulo < 292.5:
        return 6
    elif 292.5 <= angulo < 337.5:
        return 7
    else:
        return -1  # Valor para casos desconocidos

def angulo_traduccion(numero_direccion):
    direcciones = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    if 0 <= numero_direccion < len(direcciones):
        return direcciones[numero_direccion]
    else:
        return 'Desconocido'

def velocidad_a_beaufort(velocidad):
    if velocidad < 0.28:
        return 0
    elif 0.28 <= velocidad < 1.54:
        return 1
    elif 1.54 <= velocidad < 3.4:
        return 2
    elif 3.4 <= velocidad < 5.5:
        return 3
    elif 5.5 <= velocidad < 8.0:
        return 4
    elif 8.0 <= velocidad < 10.8:
        return 5
    elif 10.8 <= velocidad < 13.9:
        return 6
    elif 13.9 <= velocidad < 17.2:
        return 7
    elif 17.2 <= velocidad < 20.8:
        return 8
    elif 20.8 <= velocidad < 24.5:
        return 9
    elif 24.5 <= velocidad < 28.5:
        return 10
    elif 28.5 <= velocidad < 32.7:
        return 11
    
def altura_a_douglas(altura):
    if altura < 0.1:
        return 0
    elif 0.1 <= altura < 0.5:
        return 1
    elif 0.5 <= altura < 1.25:
        return 2
    elif 1.25 <= altura < 2.5:
        return 3
    elif 2.5 <= altura < 4.0:
        return 4
    elif 4.0 <= altura < 6.0:
        return 5
    elif 6.0 <= altura < 9.0:
        return 6
    elif 9.0 <= altura < 14.0:
        return 7
    elif 14.0 <= altura < 20.0:
        return 8

def douglas_traduccion(valor):
    douglas_dict = {
        0: 'Calma',
        1: 'Rizada',
        2: 'Marejadilla',
        3: 'Marejada',
        4: 'Fuerte marejada',
        5: 'Gruesa',
        6: 'Muy gruesa',
        7: 'Arbolada',
        8: 'Montañosa'
    }
    return douglas_dict.get(valor, 'Desconocido')

def altura_a_fondo(altura):
    if altura < 1:
        return 0
    elif 1 <= altura < 1.25:
        return 1
    elif 1.25 <= altura < 1.75:
        return 2
    elif 1.75 <= altura < 2.25:
        return 3
    elif 2.25 <= altura < 2.75:
        return 4
    elif 2.75 <= altura < 3.25:
        return 5
    elif 3.25 <= altura < 3.75:
        return 6
    elif 3.75 <= altura < 4.25:
        return 7
    elif 4.25 <= altura < 4.75:
        return 8
    elif 4.75 <= altura < 5.25:
        return 9
    elif 5.25 <= altura < 5.75:
        return 10
    elif 5.75 <= altura < 6.25:
        return 11
    elif 6.25 <= altura < 6.75:
        return 12
    elif 6.75 <= altura < 7.25:
        return 13
    elif 7.25 <= altura < 7.75:
        return 14
    elif 7.75 <= altura < 8.25:
        return 15
    elif 8.25 <= altura < 8.75:
        return 16
    elif 8.75 <= altura < 9.25:
        return 17
    else:
        return 18  # Para alturas mayores o iguales a 9.25

def fondo_traduccion(categoria):
    traducciones = {
            0: 'menos de 1 m',
            1: 'de en torno a 1 m',
            2: 'de 1 a 2 m',
            3: 'de en torno a 2 m',
            4: 'de 2 a 3 m',
            5: 'de en torno a 3 m',
            6: 'de 3 a 4 m',
            7: 'de en torno a 4 m',
            8: 'de 4 a 5 m',
            9: 'de en torno a 5 m',
            10: 'de 5 a 6 m',
            11: 'de en torno a 6 m',
            12: 'de 6 a 7 m',
            13: 'de en torno a 7 m',
            14: 'de 7 a 8 m',
            15: 'de en torno a 8 m',
            16: 'de 8 a 9 m',
            17: 'de en torno a 9 m',
            18: 'de mas de 9 m',
        }
    return traducciones.get(categoria, 'Desconocido')

def fen_traduccion(categoria, indice_fenomeno):
    if indice_fenomeno == 1:
        traducciones = {
            0: '0',
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10',
            11: '11',
            12: '12'
    }
    elif indice_fenomeno == 2:
        traducciones = {
            0: 'Calma',
            1: 'Rizada',
            2: 'Marejadilla',
            3: 'Marejada',
            4: 'Fuerte marejada',
            5: 'Gruesa',
            6: 'Muy gruesa',
            7: 'Arbolada',
            8: 'Montañosa'
    }
    elif indice_fenomeno == 3:
        traducciones = {
            0: 'menos de 1 m',
            1: 'de en torno a 1 m',
            2: 'de 1 a 2 m',
            3: 'de en torno a 2 m',
            4: 'de 2 a 3 m',
            5: 'de en torno a 3 m',
            6: 'de 3 a 4 m',
            7: 'de en torno a 4 m',
            8: 'de 4 a 5 m',
            9: 'de en torno a 5 m',
            10: 'de 5 a 6 m',
            11: 'de en torno a 6 m',
            12: 'de 6 a 7 m',
            13: 'de en torno a 7 m',
            14: 'de 7 a 8 m',
            15: 'de en torno a 8 m',
            16: 'de 8 a 9 m',
            17: 'de en torno a 9 m',
            18: 'de mas de 9 m',
        }
    return traducciones.get(categoria, 'Desconocido')
    
def tiempo_traduccion(valor, num_boletin):
    if num_boletin == 1:
        tiempo_dict = {
            0: 'al principio',
            1: 'a partir del principio de la tarde',
            2: 'a partir del final de la tarde',
            3: 'a partir del anochecer',
            4: 'a partir de medianoche',
            5: 'a partir del principio de la madrugada',
            6: 'a partir del final de la madrugada',
            7: 'a partir de la mañana',
            8: 'al final'
        }
    elif num_boletin == 2:
        tiempo_dict = {
            0: 'al principio',
            1: 'a partir del anochecer',
            2: 'a partir de medianoche',
            3: 'a partir del principio de la madrugada',
            4: 'a partir del final de la madrugada',
            5: 'a partir de la mañana',
            6: 'a partir del mediodía',
            7: 'a partir del principio de la tarde',
            8: 'al final'
        }
    return tiempo_dict.get(valor, 'Desconocido')

def primer_valor(cadena):
    # Busca el primer número en la cadena
    match = re.search(r'\d+', cadena)
    if match:
        return int(match.group())
    else:
        return None

def generar_secuencia_angulo(ang):

    primer_ang = False
    segundo_ang = False
    
    fen_ang_A = None  
    fen_ang_B = None
    
    cambio_ang = []  
    fen_ang = []  

    dbg = f"Angulo\n"

    for i in range(0, 9):
        
        ###### Ruptura y reinicio ######

        if ((primer_ang and not segundo_ang and abs(ang[i] - fen_ang_A) > 1 and abs(ang[i] - fen_ang_A) < 7)
            or (segundo_ang and ang[i] != fen_ang_A and ang[i] != fen_ang_B)):

            cambio_ang.append(i)

            if fen_ang_B is not None:
                buffer_ang = f"{angulo_traduccion(fen_ang_A)} o {angulo_traduccion(fen_ang_B)}"
            else:
                buffer_ang = f"{angulo_traduccion(fen_ang_A)}"

            fen_ang.append(buffer_ang)

            fen_ang_A = None  
            fen_ang_B = None

            primer_ang = False
            segundo_ang = False     
             
        ###### Nuevos valores ######

        if not primer_ang:
            fen_ang_A = ang[i]
            primer_ang = True       

        if primer_ang and not segundo_ang and (abs(ang[i] - fen_ang_A) == 1 or abs(ang[i] - fen_ang_A) == 7):
            fen_ang_B = ang[i]
            segundo_ang = True

        ###### DEBUGER ######
        dbg += f"i: {i}\n"
        dbg += f"fen_ang_A: {fen_ang_A}\n"
        dbg += f"fen_ang_B: {fen_ang_B}\n"
        
    if fen_ang_B is not None:
        buffer_ang = f"{angulo_traduccion(fen_ang_A)} o {angulo_traduccion(fen_ang_B)}"
    else:
        buffer_ang = angulo_traduccion(fen_ang_A)
    fen_ang.append(buffer_ang)
    primer_ang = False
    segundo_ang = False

    fen_ang_A = None  
    fen_ang_B = None

    return cambio_ang, fen_ang, dbg

def texto_valor(fen_valor_med_A, fen_valor_med_B, fen_valor_max_A, fen_valor_max_B, indice_fenomeno):

    if indice_fenomeno == 1:
        if fen_valor_med_B is None and fen_valor_max_A is None:
            buffer_valor = f"{fen_valor_med_A}"
        elif fen_valor_med_B is None and fen_valor_max_B is None:
            buffer_valor = f"{fen_valor_med_A} o {fen_valor_max_A}"
        elif fen_valor_med_B is not None and fen_valor_max_A is None:
            buffer_valor = f"{fen_valor_med_A} o {fen_valor_med_B}"
        elif fen_valor_med_B is not None and fen_valor_max_B is None:
            buffer_valor = f"{fen_valor_med_A} o {fen_valor_med_B}, localmente {fen_valor_max_A}"
        elif fen_valor_med_B is None and fen_valor_max_B is not None:
            buffer_valor = f"{fen_valor_med_A} o {fen_valor_max_A}, localmente {fen_valor_max_B}"
        elif fen_valor_med_B is not None and fen_valor_max_B is not None:
            buffer_valor = f"{fen_valor_med_A} o {fen_valor_med_B}, localmente {fen_valor_max_A} y ocasionalmente {fen_valor_max_B}"
        return buffer_valor
    
    if indice_fenomeno == 2:
        if fen_valor_med_B is None and fen_valor_max_A is None:
            buffer_valor = f"{fen_traduccion(fen_valor_med_A, indice_fenomeno)}"
            num_valor = f"{fen_valor_med_A}"
        elif fen_valor_med_B is None and fen_valor_max_B is None:
            buffer_valor = f"{fen_traduccion(fen_valor_med_A, indice_fenomeno)} o {fen_traduccion(fen_valor_max_A, indice_fenomeno).lower()}"
            num_valor = f"{fen_valor_med_A} o {fen_valor_max_A}"
        elif fen_valor_med_B is not None and fen_valor_max_A is None:
            buffer_valor = f"{fen_traduccion(fen_valor_med_A, indice_fenomeno)} o {fen_traduccion(fen_valor_med_B, indice_fenomeno).lower()}"
            num_valor = f"{fen_valor_med_A} o {fen_valor_med_B}"
        elif fen_valor_med_B is not None and fen_valor_max_B is None:
            buffer_valor = f"{fen_traduccion(fen_valor_med_A, indice_fenomeno)} o {fen_traduccion(fen_valor_med_B, indice_fenomeno).lower()}, localmente {fen_traduccion(fen_valor_max_A, indice_fenomeno).lower()}"
            num_valor = f"{fen_valor_med_A} o {fen_valor_med_B}, localmente {fen_valor_max_A}"
        elif fen_valor_med_B is None and fen_valor_max_B is not None:
            buffer_valor = f"{fen_traduccion(fen_valor_med_A, indice_fenomeno)} o {fen_traduccion(fen_valor_max_A, indice_fenomeno).lower()}, localmente {fen_traduccion(fen_valor_max_B, indice_fenomeno).lower()}"
            num_valor = f"{fen_valor_med_A} o {fen_valor_max_A}, localmente {fen_valor_max_B}"
        elif fen_valor_med_B is not None and fen_valor_max_B is not None:
            buffer_valor = f"{fen_traduccion(fen_valor_med_A, indice_fenomeno)} o {fen_traduccion(fen_valor_med_B, indice_fenomeno).lower()}, localmente {fen_traduccion(fen_valor_max_A, indice_fenomeno).lower()} y ocasionalmente {fen_traduccion(fen_valor_max_B, indice_fenomeno).lower()}"
            num_valor = f"{fen_valor_med_A} o {fen_valor_med_B}, localmente {fen_valor_max_A} y ocasionalmente {fen_valor_max_B}"
        return buffer_valor, num_valor

    if indice_fenomeno == 3:
        if fen_valor_med_B is None and fen_valor_max_A is None:
            buffer_valor = f"{fen_traduccion(fen_valor_med_A, indice_fenomeno)}" 
            num_valor = f"{fen_valor_med_A}"
        elif fen_valor_med_B is None and fen_valor_max_B is None:
            buffer_valor = f"{fen_traduccion(fen_valor_max_A, indice_fenomeno)}"
            num_valor = f"{fen_valor_max_A}"
        elif fen_valor_med_B is not None and fen_valor_max_A is None:
            buffer_valor = f"{fen_traduccion(fen_valor_med_B, indice_fenomeno)}"
            num_valor = f"{fen_valor_med_B}"
        elif fen_valor_med_B is not None and fen_valor_max_B is None:
            buffer_valor = f"{fen_traduccion(fen_valor_max_A, indice_fenomeno)}"
            num_valor = f"{fen_valor_max_A}"
        elif fen_valor_med_B is None and fen_valor_max_B is not None:
            buffer_valor = f"{fen_traduccion(fen_valor_max_B, indice_fenomeno)}"
            num_valor = f"{fen_valor_max_B}"
        elif fen_valor_med_B is not None and fen_valor_max_B is not None:
            buffer_valor = f"{fen_traduccion(fen_valor_max_B, indice_fenomeno)}"
            num_valor = f"{fen_valor_max_B}"
        return buffer_valor, num_valor
    
def generar_secuencia_valor(valor_max, valor_med, indice_fenomeno):
    
    primer_valor_med = False
    segundo_valor_med = False

    primer_valor_med_bajo = False
    segundo_valor_med_bajo = False
    
    fen_valor_med_A = None 
    fen_valor_med_B = None

    primer_valor_max = False
    segundo_valor_max = False
     
    fen_valor_max_A = None 
    fen_valor_max_B = None
    
    cambio_valor = [] 
    fen_valor = []  
    num_valor = []

    dbg = f"Valor {indice_fenomeno}\n"

    for i in range(0, 9):
        
        ###### Variables de ruptura ######

        if primer_valor_med_bajo and segundo_valor_med and valor_med[i] == (fen_valor_med_A - 1):
            segundo_valor_med_bajo = True

        if primer_valor_med_bajo and segundo_valor_med and valor_med[i] != (fen_valor_med_A - 1):
            primer_valor_med_bajo = False

        if segundo_valor_med and valor_med[i] == (fen_valor_med_A - 1):
            primer_valor_med_bajo = True
        
        ###### Condiciones de ruptura ######

        cond_1 = segundo_valor_med_bajo
        
        cond_2 = primer_valor_med and not segundo_valor_med and abs(valor_med[i] - fen_valor_med_A) > 1

        cond_3 = segundo_valor_med and valor_med[i] > fen_valor_med_B

        cond_4 = segundo_valor_med and valor_med[i] < (fen_valor_med_A - 1)
        
        cond_5 = primer_valor_max and not segundo_valor_max and valor_max[i] > (fen_valor_max_A + 1)

        cond_6 = segundo_valor_max and (valor_max[i] > fen_valor_max_B)

        ###### Ruptura y reinicio ######
            
        if (cond_1 
            or cond_2 
            or cond_3
            or cond_4 
            or cond_5
            or cond_6
            ):
            if cond_1:
                cambio_valor.append(i-1)
            else:
                cambio_valor.append(i)

            if cond_2:
                if valor_med[i] > fen_valor_med_A and not primer_valor_max:
                    fen_valor_med_B = fen_valor_med_A + 1
                    segundo_valor_med = True
                elif valor_med[i] < fen_valor_med_A and not primer_valor_max:
                    fen_valor_med_B = fen_valor_med_A 
                    fen_valor_med_A = fen_valor_med_B - 1
                    segundo_valor_med = True

            if indice_fenomeno == 1:
                buffer_valor = texto_valor(fen_valor_med_A, fen_valor_med_B, fen_valor_max_A, fen_valor_max_B, indice_fenomeno)
                fen_valor.append(buffer_valor)
            else:
                buffer_valor, buffer_num_valor = texto_valor(fen_valor_med_A, fen_valor_med_B, fen_valor_max_A, fen_valor_max_B, indice_fenomeno)
                fen_valor.append(buffer_valor)
                num_valor.append(buffer_num_valor)

            primer_valor_med = False
            segundo_valor_med = False

            primer_valor_med_bajo = False
            segundo_valor_med_bajo = False
            
            fen_valor_med_A = None 
            fen_valor_med_B = None

            primer_valor_max = False
            segundo_valor_max = False
            
            fen_valor_max_A = None 
            fen_valor_max_B = None

        ###### Nuevos valores ######

        if (not primer_valor_med 
            and not (indice_fenomeno==3 and valor_med[i] == 0)):
            fen_valor_med_A = valor_med[i]
            primer_valor_med = True

        if (((primer_valor_med and not segundo_valor_med and not primer_valor_max and valor_max[i] > fen_valor_med_A) or (segundo_valor_med and not primer_valor_max and valor_max[i] > fen_valor_med_B))
            and not (indice_fenomeno==3 and valor_med[i] == 0)):
            fen_valor_max_A = valor_max[i]
            primer_valor_max = True

        if (primer_valor_med and not segundo_valor_med and abs(valor_med[i] - fen_valor_med_A) == 1 and valor_med[i] != fen_valor_max_A
            and not (indice_fenomeno==3 and valor_med[i] == 0)):
            
            fen_valor_med_B = valor_med[i]
            if fen_valor_med_B < fen_valor_med_A:
                buffer = fen_valor_med_B
                fen_valor_med_B = fen_valor_med_A
                fen_valor_med_A = buffer
            segundo_valor_med = True

        elif (primer_valor_med and fen_valor_max_A and not segundo_valor_med and abs(valor_med[i] - fen_valor_med_A) == 1 and valor_med[i] == fen_valor_max_A
              and not (indice_fenomeno==3 and valor_med[i] == 0)):

            fen_valor_med_B = valor_med[i]
            segundo_valor_med = True
            if not segundo_valor_max:
                fen_valor_max_A = None 
                primer_valor_max = False
            else:
                fen_valor_max_A = fen_valor_max_B
                fen_valor_max_B = None 
                segundo_valor_max = False
        
        if (primer_valor_max and not segundo_valor_max and abs(valor_max[i] - fen_valor_max_A) == 1  
            and valor_max[i] != fen_valor_med_A and valor_max[i] != fen_valor_med_B
            and not (indice_fenomeno==3 and valor_max[i] == 0)):

            fen_valor_max_B = valor_max[i]
            if fen_valor_max_B < fen_valor_max_A:
                buffer = fen_valor_med_B
                fen_valor_max_B = fen_valor_max_A
                fen_valor_max_A = buffer
            segundo_valor_max = True

        if (primer_valor_max and not segundo_valor_max and segundo_valor_med and fen_valor_max_A == fen_valor_med_B + 2
            and not (indice_fenomeno==3 and valor_max[i] == 0)):
            
            fen_valor_max_B = fen_valor_max_A
            fen_valor_max_A = fen_valor_max_B - 1 
            segundo_valor_max = True

        if (primer_valor_max and not segundo_valor_med and fen_valor_max_A == fen_valor_med_A + 2
            and not (indice_fenomeno==3 and valor_max[i] == 0)):

            fen_valor_med_B = fen_valor_max_A - 1 
            segundo_valor_med = True

        ###### DEBUGER ######
        dbg += f"i: {i}\n"
        dbg += f"fen_valor_med_A: {fen_valor_med_A}\n"
        dbg += f"fen_valor_med_B: {fen_valor_med_B}\n"
        dbg += f"fen_valor_max_A: {fen_valor_max_A}\n"
        dbg += f"fen_valor_max_B: {fen_valor_max_B}\n"
        dbg += f"primer_valor_med_bajo: {primer_valor_med_bajo}\n"
        
    if indice_fenomeno == 1:
        buffer_valor = texto_valor(fen_valor_med_A, fen_valor_med_B, fen_valor_max_A, fen_valor_max_B, indice_fenomeno)
        fen_valor.append(buffer_valor)
    else:
        buffer_valor, buffer_num_valor = texto_valor(fen_valor_med_A, fen_valor_med_B, fen_valor_max_A, fen_valor_max_B, indice_fenomeno)
        fen_valor.append(buffer_valor)
        num_valor.append(buffer_num_valor)

    
    primer_valor_med = False
    segundo_valor_med = False

    primer_valor_med_bajo = False
    segundo_valor_med_bajo = False
    
    fen_valor_med_A = None 
    fen_valor_med_B = None

    primer_valor_max = False
    segundo_valor_max = False
    
    fen_valor_max_A = None 
    fen_valor_max_B = None

    if indice_fenomeno == 1:
        return cambio_valor, fen_valor, dbg
    else:
        return cambio_valor, fen_valor, num_valor, dbg

def texto_valor_shts(fen_valor_max_A, fen_valor_max_B, fen_valor_max_C):

    if fen_valor_max_B is None:
        buffer_valor = f"{fen_traduccion(fen_valor_max_A, 3)}" 
        num_valor = f"{fen_valor_max_A}"
    elif fen_valor_max_C is None:
        buffer_valor = f"{fen_traduccion(fen_valor_max_B, 3)}"
        num_valor = f"{fen_valor_max_B}"
    elif fen_valor_max_C is not None:
        buffer_valor = f"{fen_traduccion(fen_valor_max_C, 3)}"
        num_valor = f"{fen_valor_max_C}"
    return buffer_valor, num_valor

def generar_secuencia_shts(valor):
    

    primer_bajo = False
    segundo_bajo = False

    primer_valor = False
    segundo_valor = False
    tercer_valor = False
     
    fen_valor_A = None 
    fen_valor_B = None
    fen_valor_C = None
    
    cambio_valor = [] 
    fen_valor = []  
    num_valor = []

    dbg = f"Valor shts\n"
    dbg += f"{valor}\n"

    for i in range(0, 9):

        ###### Variables de ruptura ######

        cond_0 = (primer_valor and not segundo_valor and fen_valor_A - valor[i] == 3) or (segundo_valor and not tercer_valor and fen_valor_B - valor[i] == 3) or (tercer_valor and fen_valor_C - valor[i] == 3)
        
        if cond_0 and primer_bajo:
            segundo_bajo = True

        if not cond_0 and primer_bajo:
            segundo_bajo = False

        if cond_0:
            primer_bajo = True

        ###### Condiciones de ruptura ######
        
        cond_1 = primer_valor and not segundo_valor and (valor[i] - fen_valor_A > 2 or (fen_valor_A - valor[i] > 3) or (fen_valor_A - valor[i] == 3 and segundo_bajo))

        cond_2 = segundo_valor and not tercer_valor and (valor[i] - fen_valor_A > 2 or (fen_valor_B - valor[i] > 3) or (fen_valor_B - valor[i] == 3 and segundo_bajo))

        cond_3 = tercer_valor and (valor[i] - fen_valor_A > 2 or (fen_valor_C - valor[i] > 3) or (fen_valor_C - valor[i] == 3 and segundo_bajo))

        ###### Ruptura y reinicio ######
            
        if (cond_1 
            or cond_2
            or cond_3
            ):
            if segundo_bajo:
                cambio_valor.append(i-1)
            else:
                cambio_valor.append(i)

            buffer_valor, buffer_num_valor = texto_valor_shts(fen_valor_A, fen_valor_B, fen_valor_C)
            fen_valor.append(buffer_valor)
            num_valor.append(buffer_num_valor)

            primer_bajo = False
            segundo_bajo = False

            primer_valor = False
            segundo_valor = False
            tercer_valor = False
            
            fen_valor_A = None 
            fen_valor_B = None
            fen_valor_C = None

        ###### Nuevos valores ######

        if (not primer_valor and not valor[i] == 0):
            
            fen_valor_A = valor[i]
            primer_valor = True

        if (primer_valor and not segundo_valor and valor[i] != fen_valor_A and not valor[i] == 0):
            
            fen_valor_B = valor[i]

            if fen_valor_B < fen_valor_A:
                buffer = fen_valor_B
                fen_valor_B = fen_valor_A
                fen_valor_A = buffer
            segundo_valor = True

        if (segundo_valor and not tercer_valor and valor[i] != fen_valor_A and valor[i] != fen_valor_B and not valor[i] == 0):
            
            fen_valor_C = valor[i]

            if fen_valor_C < fen_valor_A:
                buffer = fen_valor_C
                fen_valor_C = fen_valor_B
                fen_valor_B = fen_valor_A
                fen_valor_A = buffer

            if fen_valor_A < fen_valor_C < fen_valor_B:
                buffer = fen_valor_C
                fen_valor_C = fen_valor_B
                fen_valor_B = buffer
            
            tercer_valor = True

        ###### DEBUGER ######
        dbg += f"i: {i}\n"
        dbg += f"fen_valor_A: {fen_valor_A}\n"
        dbg += f"fen_valor_B: {fen_valor_B}\n"
        dbg += f"fen_valor_C: {fen_valor_C}\n"
        dbg += f"primer_valor_med_bajo: {primer_bajo}\n"
        
    buffer_valor, buffer_num_valor = texto_valor_shts(fen_valor_A, fen_valor_B, fen_valor_C)
    fen_valor.append(buffer_valor)
    num_valor.append(buffer_num_valor)

    primer_bajo = False
    segundo_bajo = False

    primer_valor = False
    segundo_valor = False
    tercer_valor = False
    
    fen_valor_A = None 
    fen_valor_B = None
    fen_valor_C = None

    return cambio_valor, fen_valor, num_valor, dbg
    
def filtrar_repetidos(lista_cambio, lista_fen):
    i=0
    while i < len(lista_fen) - 1:
        if lista_fen[i] == lista_fen[i+1]:
            del lista_fen[i+1]
            del lista_cambio[i]
        else:
            i+= 1
    
def texto_boletin_viento(dwi, wind_max, wind_med, num_boletin):

    cambio_dwi = []  
    fen_dwi = []

    cambio_dwi, fen_dwi, dbg = generar_secuencia_angulo(dwi)

    dbg += f"cambio_dwi: {cambio_dwi}\n"
    dbg += f"fen_dwi: {fen_dwi}\n"

    cambio_wind = [] 
    fen_wind = []

    cambio_wind, fen_wind, dbg_mas = generar_secuencia_valor(wind_max, wind_med, 1)
    dbg += dbg_mas

    cambios_totales = []
    cambios_totales = sorted(set(cambio_dwi + cambio_wind))

    dbg += f"cambio_wind: {cambio_wind}\n"
    dbg += f"fen_wind: {fen_wind}\n"
    dbg += f"cambios_totales: {cambios_totales}\n"

    texto_boletin = f"{fen_dwi[0]} {fen_wind[0]}"
    j=0
    k=0

    for i in range(len(cambios_totales)):
        if cambios_totales[i] in cambio_dwi and cambios_totales[i] in cambio_wind:
            j+=1
            k+=1
            if primer_valor(fen_wind[k-1]) > primer_valor(fen_wind[k]):
                texto_boletin += f", amainando a {fen_dwi[j]} {fen_wind[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
            elif primer_valor(fen_wind[k-1]) < primer_valor(fen_wind[k]):
                texto_boletin += f", arreciando a {fen_dwi[j]} {fen_wind[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
            elif primer_valor(fen_wind[k-1]) > primer_valor(fen_wind[k]):
                texto_boletin += f", rolando a {fen_dwi[j]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
        elif cambios_totales[i] in cambio_dwi and not cambios_totales[i] in cambio_wind:
            j+=1
            texto_boletin += f", rolando a {fen_dwi[j]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
        elif not cambios_totales[i] in cambio_dwi and cambios_totales[i] in cambio_wind:
            k+=1
            if primer_valor(fen_wind[k-1]) > primer_valor(fen_wind[k]):
                texto_boletin += f", amainando a {fen_wind[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
            elif primer_valor(fen_wind[k-1]) < primer_valor(fen_wind[k]):
                texto_boletin += f", arreciando a {fen_wind[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"

    texto_boletin += f". "
    
    return texto_boletin, dbg

def texto_boletin_mar_viento(shww_max, shww_med, num_boletin):

    cambio_shww = [] 
    fen_shww = []
    num_shww = []

    cambio_shww, fen_shww, num_shww, dbg = generar_secuencia_valor(shww_max, shww_med, 2)

    dbg += f"cambio_shww: {cambio_shww}\n"
    dbg += f"fen_shww: {fen_shww}\n"
    dbg += f"num_shww: {num_shww}\n"

    texto_boletin = f"{fen_shww[0]}"
    texto_prueba = f"{num_shww[0]}"

    for i in range(len(cambio_shww)):

        if primer_valor(num_shww[i]) > primer_valor(num_shww[i+1]):
            texto_boletin += f", disminuyendo a {fen_shww[i+1].lower()} {tiempo_traduccion(cambio_shww[i], num_boletin)}"
            texto_prueba += f", disminuyendo a {num_shww[i+1].lower()} {tiempo_traduccion(cambio_shww[i], num_boletin)}"
        elif primer_valor(num_shww[i]) < primer_valor(num_shww[i+1]):
            texto_boletin += f", aumentando a {fen_shww[i+1].lower()} {tiempo_traduccion(cambio_shww[i], num_boletin)}"
            texto_prueba += f", aumentando a {num_shww[i+1].lower()} {tiempo_traduccion(cambio_shww[i], num_boletin)}"
    
    texto_boletin += f". "
    texto_prueba += f". "

    return texto_boletin, texto_prueba, dbg

def texto_boletin_mar_fondo(mdts, shts_max, shts_med, num_boletin):

    cambio_mdts = []  
    fen_mdts = []

    cambio_mdts, fen_mdts, dbg = generar_secuencia_angulo(mdts)

    dbg += f"cambio_mdts: {cambio_mdts}\n"
    dbg += f"fen_mdts: {fen_mdts}\n"

    cambio_shts = [] 
    fen_shts = []
    num_shts = []

    # cambio_shts, fen_shts, num_shts, dbg_mas = generar_secuencia_valor(shts_max, shts_med, 3)
    # dbg += dbg_mas

    cambio_shts, fen_shts, num_shts, dbg_mas = generar_secuencia_shts(shts_med)
    dbg += dbg_mas

    filtrar_repetidos(cambio_shts, num_shts)

    cambios_totales = []
    cambios_totales = sorted(set(cambio_mdts + cambio_shts))

    dbg += f"cambio_shts: {cambio_shts}\n"
    dbg += f"fen_shts: {fen_shts}\n"
    dbg += f"num_shts: {num_shts}\n"
    dbg += f"cambios_totales: {cambios_totales}\n"

    texto_boletin = f"Mar de fondo del {fen_mdts[0]} {fen_shts[0]}"
    texto_prueba = f"Mar de fondo del {fen_mdts[0]} {num_shts[0]}"
    j=0
    k=0

    for i in range(len(cambios_totales)):
        if cambios_totales[i] in cambio_mdts and cambios_totales[i] in cambio_shts:
            j+=1
            k+=1
            if primer_valor(num_shts[k-1]) > primer_valor(num_shts[k]):
                texto_boletin += f", disminuyendo a {fen_mdts[j]} {fen_shts[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
                texto_prueba += f", disminuyendo a {fen_mdts[j]} {num_shts[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
            elif primer_valor(num_shts[k-1]) < primer_valor(num_shts[k]):
                texto_boletin += f", aumentando a {fen_mdts[j]} {fen_shts[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
                texto_prueba += f", aumentando a {fen_mdts[j]} {num_shts[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
            elif primer_valor(num_shts[k-1]) > primer_valor(num_shts[k]):
                texto_boletin += f", girando a {fen_mdts[j]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
                texto_prueba += f", girando a {fen_mdts[j]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
        elif cambios_totales[i] in cambio_mdts and not cambios_totales[i] in cambio_shts:
            j+=1
            texto_boletin += f", girando a {fen_mdts[j]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
            texto_prueba += f", girando a {fen_mdts[j]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
        elif not cambios_totales[i] in cambio_mdts and cambios_totales[i] in cambio_shts:
            k+=1
            if primer_valor(num_shts[k-1]) > primer_valor(num_shts[k]):
                texto_boletin += f", disminuyendo a {fen_shts[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
                texto_prueba += f", disminuyendo a {num_shts[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
            elif primer_valor(num_shts[k-1]) < primer_valor(num_shts[k]):
                texto_boletin += f", aumentando a {fen_shts[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"
                texto_prueba += f", aumentando a {num_shts[k]} {tiempo_traduccion(cambios_totales[i], num_boletin)}"

    texto_boletin += f". "
    texto_prueba += f". "

    return texto_boletin, texto_prueba, dbg

def operar_prediccion(boletin_csv):

    emission_time = boletin_csv['emission_time'].iloc[0]

    dia = emission_time[:10].replace('-', '')  
    hora_emision = emission_time[11:16].replace(':', '')  

    if hora_emision == '1200':
        num_boletin = 1
    elif hora_emision == '1800':
        num_boletin = 2
    else:
        print('Hay un problema con los boletines')

    boletin_csv = boletin_csv.copy()

    boletin_csv.loc[:, 'dwi'] = boletin_csv.apply(lambda row: reconstruir_angulo(row['dwi_sin'], row['dwi_cos']), axis=1)
    boletin_csv.loc[:, 'mdts'] = boletin_csv.apply(lambda row: reconstruir_angulo(row['mdts_sin'], row['mdts_cos']), axis=1)

    boletin_csv.loc[:, 'dwi'] = boletin_csv['dwi'].apply(clasificar_angulo)#.apply(angulo_traduccion)
    boletin_csv.loc[:, 'mdts'] = boletin_csv['mdts'].apply(clasificar_angulo)#.apply(angulo_traduccion)

    boletin_csv.loc[:, 'wind_max'] = boletin_csv['wind_max'].apply(velocidad_a_beaufort)
    boletin_csv.loc[:, 'wind_med'] = boletin_csv['wind_med'].apply(velocidad_a_beaufort)

    boletin_csv.loc[:, 'shww_max'] = boletin_csv['shww_max'].apply(altura_a_douglas)#.apply(douglas_traduccion)
    boletin_csv.loc[:, 'shww_med'] = boletin_csv['shww_med'].apply(altura_a_douglas)#.apply(douglas_traduccion)

    # boletin_csv.loc[:, 'shts_max_n'] = boletin_csv['shts_max']#.apply(altura_a_fondo)#.apply(fondo_traduccion)
    # boletin_csv.loc[:, 'shts_med_n'] = boletin_csv['shts_med']#.apply(altura_a_fondo)#.apply(fondo_traduccion)

    boletin_csv.loc[:, 'shts_max'] = boletin_csv['shts_max'].apply(altura_a_fondo)#.apply(fondo_traduccion)
    boletin_csv.loc[:, 'shts_med'] = boletin_csv['shts_med'].apply(altura_a_fondo)#.apply(fondo_traduccion)

    boletin_csv = boletin_csv.drop(['emission_time', 'valid_time', 'dwi_sin', 'dwi_cos', 'mdts_sin', 'mdts_cos'], axis=1)

    boletin_csv = boletin_csv[['dwi', 'wind_max', 'wind_med', 'shww_max', 'shww_med', 'mdts', 'shts_max', 'shts_med']]#, 'shts_max_n', 'shts_med_n'
    
    texto_boletin, dbg = texto_boletin_viento(boletin_csv['dwi'], boletin_csv['wind_max'], boletin_csv['wind_med'], num_boletin)
    
    texto_prueba = texto_boletin

    texto_boletin_mar, texto_prueba_mar, dbg_mas = texto_boletin_mar_viento(boletin_csv['shww_max'], boletin_csv['shww_med'], num_boletin)
    texto_boletin += texto_boletin_mar
    texto_prueba += texto_prueba_mar
    dbg += dbg_mas

    texto_boletin_mar, texto_prueba_mar, dbg_mas = texto_boletin_mar_fondo(boletin_csv['mdts'], boletin_csv['shts_max'], boletin_csv['shts_med'], num_boletin)
    texto_boletin += texto_boletin_mar
    texto_prueba += texto_prueba_mar
    dbg += dbg_mas

    tabla_boletin = boletin_csv.to_string(index=False)

    return tabla_boletin, texto_boletin, texto_prueba, dia, hora_emision, dbg