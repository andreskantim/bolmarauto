import re
import csv
import os
import shutil
import pandas as pd
from datetime import datetime, timedelta
import math 
from math import sqrt, atan2, degrees
from itertools import product

def vaciar_directorio(directorio):
    
    shutil.rmtree(directorio, ignore_errors=True)
    
    os.makedirs(directorio, exist_ok=True)

def ordenar_claves_segun_linea(pattern, text):
    # print(pattern, text)
    match = re.search(pattern, text, re.IGNORECASE)
    return match.start() if match else float('inf')

def parametros_zonas_y_divisiones(cod_boletin): #se encarga de coger el boletin ya filtrado por zonas y foltrarlo por fenomenos en viento, mar de viendo, mar de fondo, meteoros y visibilidad
    
    num_zonas = claves_zonas_y_divisiones(None, cod_boletin, 1)
    num_divisiones = claves_zonas_y_divisiones(None, cod_boletin, 2)


    div_por_zona = {i: [] for i in range(num_zonas)}  
    dic_divisiones = {i: [] for i in range(num_zonas)}
    nombre_division = {i: [] for i in range(num_divisiones)}  
    nombre_zona = {i: [] for i in range(num_divisiones)}  
    zona_de_la_division = {i: [] for i in range(num_divisiones)}  
    
    k = 0
    
    for i in range(num_zonas):
        dic_divisiones[i] = (claves_zonas_y_divisiones(i, cod_boletin, 2))
        div_por_zona[i] = len(dic_divisiones[i])
        if div_por_zona[i] == 1:
            nombre_division[k] = dic_divisiones[i][0]
            zona_de_la_division[k] = i
            nombre_zona[k] = claves_zonas_y_divisiones(zona_de_la_division[k], cod_boletin, 1)
            k+=1
        else:
            for l in range(0, div_por_zona[i]):
                nombre_division[k] = dic_divisiones[i][l]
                zona_de_la_division[k] = i
                nombre_zona[k] = claves_zonas_y_divisiones(zona_de_la_division[k], cod_boletin, 1)
                k+=1

    return num_zonas, num_divisiones, div_por_zona, dic_divisiones, zona_de_la_division, nombre_division, nombre_zona

def claves_zonas_y_divisiones(valor, cod_boletin, funcion):
    
        # cadiz_algeciras "36.25/-5.30/35.62/-4.92,"
        # cadiz_tarifa_este "36.03/-5.60/35.90/-5.34,"
        # cadiz_tarifa_oeste "36.05/-5.98/35.79/-5.60,"
        # cadiz_trafalgar "36.17/-6.50/35.79/-5.87,"
        # cadiz_ciudad "36.66/-6.91/36.15/-6.40,"
        # huelva_este "36.92/-6.81/36.66/-6.43,"
        # huelva_oeste "37.15/-7.40/36.77/-6.81,"    
        # pontevedra "42.50/-9.51/41.83/-9.00,"
        # coruña_oeste "43.51/-9.76/42.50/-9.25,"
        # coruña_noroeste "43.86/-9.37/43.35/-8.36,"
        # coruña_norte "44.21/-8.41/43.70/-7.65,"
        # lugo "44.18/-7.65/43.67/-7.02,"
        # asturias_oeste "44.01/-7.02/43.50/-5.85,"
        # asturias_este "44.01/-5.85/43.50/-4.51,"
        # asturias "44.01/-7.02/43.50/-4.51,"
        # cantabria "43.84/-4.51/43.46/-3.16,"
        # vizcaya "43.84/-3.16/43.46/-2.39,"
        # guipuzcua "43.84/-2.39/43.46/-1.70,"
        
    if cod_boletin == "FQXX40MM":

        if funcion == 1: 
            dic = {
                0: "lugo",
                1: "coruña",
                2: "pontevedra" 
            }
        if funcion == 2:
            dic = {
                0: [0],
                1: ["norte", "sur"],
                2: [0]
            }

    elif cod_boletin == "FQXX41MM":
        
        if funcion == 1: 
            dic = {
                0: "asturias",
                1: "cantabria",
                2: "vizcaya",
                3: "guipuzcua"
            }
        if funcion == 2:
            dic = {
                0: ["oeste", "este"],
                1: [0],
                2: [0],
                3: [0]
            }

    elif cod_boletin == "FQXX42MM":
        
        if funcion == 1: 
            dic = {
                0: "huelva",
                1: "cadiz",   
            }
        if funcion == 2:
            dic = {
                0: [0],
                1: ["ciudad", "trafalgar", "tarifa", "algeciras"],   
            }
    else:
        dic = {}
    
    if valor is None:
        if funcion == 1:
           return len(dic)
        elif funcion == 2:
            return sum(len(v) if isinstance(v, list) else 1 for k, v in dic.items())

    if funcion == 1:
        return dic.get(valor)
    if funcion == 2:
        return dic.get(valor)

def claves_generar_lineas(): #Separar las lineas del boletin cuando falten los puntos finales

    opcional_cerca_costa = r"(?:CERCA\s*DE\s*LA\s*COSTA|EN\s*LA\s*COSTA)?\s*"
        
    obligatorio_proximidades = r"\b(?:EN\s*TORNO\s*(?:A|AL)?|CERCA\s*(?:DE|DEL)?|EN\s*LAS\s*PROXIMIDADES\s*(?:DE|DEL)?|EN\s*EL\s*AREA\s*(?:DE|DEL)?|EN)\s*"

    area = r"NORTE|SUR|OESTE|OCCIDENTAL|ESTE|ORIENTAL"

    claves= [
        
        #Todas las zonas
        r"(?:-|;)\s*(EN)?\s*(?:AMBAS\s*ZONAS|TODAS?\s*LAS?\s*ZONAS?|TODO\s*EL\s*LITORAL)",
        
        #Resto
        r"(?:-|;)\s*(?:EN)?\s*(?:EL)?(?:RESTO)",

        # General
        fr"(?:-|;)\s*{opcional_cerca_costa}(?:AL\s*|(EN)?\s*EL\s*)?(?:EXTREMO\s*|LITOR?AL\s*)?(?:{area})", 
        
        # Exclusión de zonas
        fr"(?:-|;)\s*{opcional_cerca_costa}EXCEPTO\s*AL\s*(?:{area})",
        
        # En torno a puntos clave 
        fr"(?:-|;)\s*{opcional_cerca_costa}{obligatorio_proximidades}",
        
        # De un punto a (otro | hacia el área)
        fr"(?:-|;)\s*{opcional_cerca_costa}(?:DESDE|ENTRE\s*|DE\s*)",
    
    ] 
        
    return claves

def claves_ordenar_por_zonas(cod_boletin, zona, nombre_division, div_por_zona, funcion): 

    #A la hora de escribir claves, solo importa aquello que esta entre las partes obligatorias
    #Si ademas es una clave inicial, tambien importa lo que este antes de la primera parte obligatoria

    add_claves_principio = []

    add_claves = []

    opcional_cerca_costa = r"(?:CERCA\s*DE\s*LA\s*COSTA|EN\s*LA\s*COSTA)?\s*"

    opcional_cabo = r"(?:(?:CABO|PUNTA)\s*(DE\s*)?)?"

    obligatorio_proximidades = r"\b(?:EN\s*TORNO\s*(?:A|AL)?|CERCA\s*(?:DE|DEL)?|EN\s*LAS\s*PROXIMIDADES\s*(?:DE|DEL)?|EN\s*EL\s*AREA\s*(?:DE|DEL)?|EN)\s*"

    if cod_boletin == "FQXX40MM":
        if zona == 1:
            id_norte = r"(?:ESTACA\s*DE\s*)?BARES|ORTEGAL|PRIOR|PRIORINO|FERROL|CORUNA|CAION|SISARGAS|SAN\s*ADRIAN|VILAN"
            id_separacion = r"SISARGAS|VILAN|FISTERRA|SAN\s*ADRIAN|TOURINAN"
            id_sur = r"FISTERRA|CORRUBEDO|TOURINAN"
        
            if nombre_division == "norte":
                id_principal = id_norte 
                id_contrario = id_sur 

                add_claves_principio = [
                    #Hacia el oeste/este de los puntos
                    fr"{opcional_cerca_costa}(?:AL|(EN)?\s*EL\s*)?\bESTE\s*(Y\s*NORTE\s*)?DEL?\s*{opcional_cabo}(?:{id_separacion})",        
                ]
                add_claves = [  
                    fr"(?<!DESDE\s*EL\s*)\bESTE\s*(DEL?)?\s*{opcional_cabo}(?:{id_principal}|{id_separacion})",   
                ]

            elif nombre_division == "sur":
                id_principal = id_sur  
                id_contrario = id_norte

                add_claves_principio = [
                    fr"{opcional_cerca_costa}(?:AL|(EN)?\s*EL\s*)?OESTE\s*(Y\s*NORTE\s*)?DEL?\s*{opcional_cabo}(?:{id_separacion})",        
                ]
                add_claves = [  
                    fr"(?<!DESDE\s*EL\s*)OESTE\s*(DEL?)?\s*{opcional_cabo}(?:{id_principal}|{id_separacion})",   
                ]

    elif cod_boletin == "FQXX41MM":
        if zona == 0:
            id_oeste = r"BUSTOS|RIBADEO"
            id_separacion = r"BUSTOS|PENAS"
            id_este = r"LASTRES|PENAS"

            if nombre_division == "oeste":
                id_principal = id_oeste 
                id_contrario = id_este 

            elif nombre_division == "este":
                id_principal = id_este  
                id_contrario = id_oeste
        
    area = {
        "no_zona": "valor_para_no_zona",
        "resto": "valor_para_resto",
        "norte": "NORTE",
        "sur": "SUR",
        "oeste": "OESTE|OCCIDENTAL",
        "este": "ESTE|ORIENTAL"
    }.get(nombre_division, "valor_por_defecto")
    
    neg_area = {
        "no_zona": "valor_para_no_zona",
        "resto": "valor_para_resto",
        "norte": "SUR",
        "sur": "NORTE",
        "oeste": "ESTE|ORIENTAL",
        "este": "OESTE|OCCIDENTAL"
    }.get(nombre_division, "valor_por_defecto")

    if cod_boletin == "FQXX42MM":

        if nombre_division == "ciudad":
            claves_principio = [
                "- DE GUADALQUIVIR",      
            ] 
            claves = [
            ]
            
        elif nombre_division == "trafalgar":
            claves_principio = [
                "- DE CABO ROCHE",
            ]
            claves = [
            ]
        
        elif nombre_division == "tarifa":
            claves_principio = [
                "- DE PUNTA CAMARINAL",
            ]
            claves = [
            ]
            
        elif nombre_division == "algeciras":
            claves_principio = [
                "- DE PUNTA CARNERO",
            ]
            claves = [
            ]
    else:

        if nombre_division == "no_zona":
            claves_principio = [
                r"-?\s*(EN)?\s*(?:AMBAS\s*ZONAS|TODAS?\s*LAS?\s*ZONAS?|TODO\s*EL\s*LITORAL)",
            ]
            claves = [
                r"(EN)?\s*(?:AMBAS\s*ZONAS|TODAS?\s*LAS?\s*ZONAS?|TODO\s*EL\s*LITORAL)",
            ]
            
        elif nombre_division == "resto":
            claves_principio = [
                r"-?\s*(?:EN)?\s*(?:EL)?(?:RESTO)",  
            ]
            claves = [
                r"\bEN\s*(?:EL\s*RESTO)",  
            ]      


        elif div_por_zona == 2:

            claves_principio = [
                # General
                fr"-?\s*{opcional_cerca_costa}(?:AL\s*|(EN)?\s*EL\s*)?(?:EXTREMO\s*|LITOR?AL\s*)?(?:{area})", 
                
                # Exclusión de zonas -> COMPLETAR SI ES NECESARIO
                fr"-?\s*{opcional_cerca_costa}EXCEPTO\s*AL\s*(?:{neg_area})\s*DE\s*(?:{id_contrario}|{id_separacion})",
                
                # En torno a puntos clave 
                fr"-?\s*{opcional_cerca_costa}{obligatorio_proximidades}{opcional_cabo}(?:{id_principal})",
                
                # De un punto a (otro | hacia el área)
                fr"-?\s*{opcional_cerca_costa}(?:DESDE|ENTRE\s*|DE\s*){opcional_cabo}(?:{id_principal})"
                fr"(?:(?:\s*(?:Y|-|A)\s*{opcional_cabo}(?:{id_principal}))|(?:HACIAs*EL|AL|Y\s*AL)\s*(?:{area}))",
                
                fr"-?\s*{opcional_cerca_costa}(?:DESDE|ENTRE\s*|DE\s*){opcional_cabo}(?:{id_principal}|{id_separacion})"
                fr"(?:(?:\s*(?:Y|-|A)\s*{opcional_cabo}(?:{id_principal}|{id_separacion}))|(?:HACIAs*EL|AL|Y\s*AL)\s*(?:{area}))",
            ]

            claves = [
                # General
                fr"(?<!EXCEPTO\s){opcional_cerca_costa}(?:AL|EN\s*EL|HACIA\s*EL|POR\s*EL)\s*(?:EXTREMO\s*|LITOR?AL\s*)?(?:{area})", 

                # NEGADA General
                fr"EXCEPTO\s*{opcional_cerca_costa}(?:AL|EN\s*EL|HACIA\s*EL|POR\s*EL)\s*(?:EXTREMO\s*|LITOR?AL\s*)?(?:{neg_area})", 

                # General para la zona
                fr"(?<!DESDE\sEL\s)(?:{area})\s*(?:DEL?)?\s*{opcional_cabo}(?:{id_principal}|{id_separacion})",     

                # En torno a puntos clave
                fr"(?<!EXCEPTO\s){opcional_cerca_costa}{obligatorio_proximidades}{opcional_cabo}(?:{id_principal})",

                # NEGADA En torno a puntos clave
                fr"EXCEPTO\s*{opcional_cerca_costa}{obligatorio_proximidades}{opcional_cabo}(?:{id_contrario})",
                
                # De un punto a (otro | hacia el área)
                fr"(?<!EXCEPTO\s){opcional_cerca_costa}(?:DESDE|ENTRE\s*|DE\s*){opcional_cabo}(?:{id_principal}|{id_separacion})"
                fr"(?:(?:\s*(?:Y|-|A)\s*{opcional_cabo}(?:{id_principal}))|(?:HACIAs*EL|AL|Y\s*AL)\s*(?:{area}))",

                fr"(?<!EXCEPTO\s){opcional_cerca_costa}(?:DESDE|ENTRE\s*|DE\s*){opcional_cabo}(?:{id_principal})"
                fr"(?:(?:\s*(?:Y|-|A)\s*{opcional_cabo}(?:{id_principal}|{id_separacion}))|(?:HACIAs*EL|AL|Y\s*AL)\s*(?:{area}))",

                # NEGADA De un punto a (otro | hacia el área) negadas
                fr"EXCEPTO\s*{opcional_cerca_costa}(?:DESDE|ENTRE\s*|DE\s*){opcional_cabo}(?:{id_contrario}|{id_separacion})"
                fr"(?:(?:\s*(?:Y|-|A)\s*{opcional_cabo}(?:{id_contrario}))|(?:HACIAs*EL|AL|Y\s*AL)\s*(?:{neg_area}))",
                
                fr"EXCEPTO\s*{opcional_cerca_costa}(?:DESDE|ENTRE\s*|DE\s*){opcional_cabo}(?:{id_contrario})"
                fr"(?:(?:\s*(?:Y|-|A)\s*{opcional_cabo}(?:{id_contrario}|{id_separacion}))|(?:HACIAs*EL|AL|Y\s*AL)\s*(?:{neg_area}))",
            ]
                
    if add_claves_principio:
        claves_principio.extend(add_claves_principio)

    if add_claves:
        claves.extend(add_claves)
    
    if funcion == 0:
        return claves_principio, claves
    if funcion == 1:
        return claves_principio
    if funcion == 2:
        return claves

def claves_ordenar_lineas_por_tipo_fenomeno(fenomeno):

    if fenomeno == 0:
        claves = [
            r"\b(?<!AL\s)(?<!EN\sEL\s)(?<!EXTREMO\s)(?<!HACIA\sEL\s)(?<!POR\sEL\s)(?<!DEL\s)(?<!O\s)"
            r"\b(?:NORTE|SUR|ESTE|OESTE|SUROESTE|NOROESTE|SURESTE|NORESTE|NORDESTE|N|S|E|W|NE|NW|SE|SW|VARIABLE|VRB)\b"
            r"\b\s(?!DE)",

            r"\b(?<!DE\s)"
            r"(\d)\s?((a|o)\s?\d)\b"
            r"\b\s(?!M|METROS)\b",
            
            r"FUERZA",      
        ]

    elif fenomeno == 1:
        claves = [
            r"(?:FUERTE\s*MA(?:RE{1,2})?JADA|MA(?:RE{1,2})?JADILLA|RIZADA|MA(?:RE{1,2})?JADA|MUY\s*GRUESA|GRUESA|ARBOLADA|MONTANOSA|ENORME)\b",

        ]

    elif fenomeno == 2:
        claves = [
            r"(?:MAR(?:E)?\s*(?:DE)?\s*FONDO|DE\s*FONDO)",
            
        ]

    elif fenomeno == 3: 
        claves = [
            r"(?:AGUACEROS?|TORMENTAS?|L?LUVIA|LLOVIZNA|RACHAS|PRECIPITACION)",
        ]

    elif fenomeno == 4:
        claves = [
            r"(?:VISIBILIDAD|RE?GULAR|BUENA|MALA|BRUMA|CALIMA|NIEBLA)",
        ]
    
    return claves

def claves_separar_lineas_temporalmente():

    claves = [

        # Opcional (?:Y|,)
        r"(?:Y|,)?\s*(?:TENDIENDO|AMAINANDO|ARRECIANDO|DISMINUYENDO|AUMENTANDO|TEMPORALMENTE|LOCALMENTE|OCASIONALMENTE|"
        r"ROLANDO|QUEDANDO|PREDOMINANDO|SIENDO|GENERALIZANDOSE|SALVO|POSIBILIDAD|PROBABILIDAD|PREDOMINIO|AREAS)",

        # Obligatorio (?:Y|,)
        r"(?:Y|,)\s*(?:\d+|DE\s+\d+|A\s+|EXCEPTO)",

        # Obligatorio (?:Y)
        r"(?:Y)\s*(?:MAS\s*TARDE[^\.]|AL\s*PRINCIPIO[^\.]|AL\s*FINAL[^\.]|EN\s*TODA\s*LA\s*ZONA[^\.]|EN\s*EL\s*RESTO[^\.])",

        # Opcional (?:Y|,| )
        r"(?:Y|,|\s)\s*CON\b",

        # Cambio direccional, Obligatorio (?:,)
        r"(?:,)\s*(?:NORTE|SUR|ESTE|OESTE|SUROESTE|NOROESTE|SURESTE|NORESTE|NORDESTE|N|S|E|W|NE|NW|SE|SW|VARIABLE|VRB)\b",

        # Cambio direccional empezando por separadores temporales
        r"(?:AL\s*FINAL|AL\s*PRINCIPIO|MAS\s*TARDE|EN\s*TODA\s*LA\s*ZONA|EN\s*EL\s*RESTO)\s*(?:DE\s*LA|DEL)?\s*"
        r"(?:TARDE|MANANA|DIA|MADRUGADA|MEDIODIA|NOCHE)?\s*(?:AREAS\s*DE)?\s*"
        r"(?:NORTE|SUR|ESTE|OESTE|SUROESTE|NOROESTE|SURESTE|NORESTE|NORDESTE|N|S|E|W|NE|NW|SE|SW|VARIABLE|VRB)\b",

        # Cambio intensidad mar de viento, Obligatorio (?:,)
        r"(?:,)\s*(?:FUERTE\s*MA(?:RE{1,2})?JADA|MA(?:RE{1,2})?JADILLA|RIZADA|MA(?:RE{1,2})?JADA|MUY\s*GRUESA|GRUESA|ARBOLADA|MONTANOSA|ENORME)",

        # Cambio intensidad mar de viento por separadores temporales
        r"(?:AL\s*FINAL|AL\s*PRINCIPIO|MAS\s*TARDE|EN\s*TODA\S?\s*LA\S?\s*ZONA\S?|EN\s*AMBAS\s*ZONAS|EN\s*EL\s*RESTO)\s*"
        r"(?:DE\s*LA|DEL)?\s*(?:TARDE|MANANA|DIA|MADRUGADA|MEDIODIA|NOCHE)?\s*(?:AREAS\s*DE|INTERVALOS\s*DE)?\s*"
        r"(?:FUERTE\s*MA(?:RE{1,2})?JADA|MA(?:RE{1,2})?JADILLA|RIZADA|MA(?:RE{1,2})?JADA|MUY\s*GRUESA|GRUESA|ARBOLADA|MONTANOSA|ENORME)",

        # Cambio meteoros, Obligatorio (?:,)
        r"(?:,)\s*(?:AGUACEROS?|TORMENTAS?|L?LUVIA|LLOVIZNA|RACHAS|PRECIPITACION)",

        # Cambio meteoros por separadores temporales
        r"(?:AL\s*FINAL|AL\s*PRINCIPIO|MAS\s*TARDE|EN\s*TODA\S?\s*LA\S?\s*ZONA\S?|EN\s*AMBAS\s*ZONAS|EN\s*EL\s*RESTO)\s*"
        r"(?:DE\s*LA|DEL)?\s*(?:TARDE|MANANA|DIA|MADRUGADA|MEDIODIA|NOCHE)?\s*(?:AREAS\s*DE|INTERVALOS\s*DE)?\s*"
        r"(?:AGUACEROS?|TORMENTAS?|L?LUVIA|LLOVIZNA|RACHAS|PRECIPITACION)",

        # Cambio visibilidad, Obligatorio (?:,)
        r"(?:,)\s*(?:VISIBILIDAD|RE?GULAR|BUENA|MALA|BRUMA|CALIMA|NIEBLA)",

        # Cambio visibilidad por separadores temporales
        r"(?:AL\s*FINAL|AL\s*PRINCIPIO|MAS\s*TARDE|EN\s*TODA\S?\s*LA\S?\s*ZONA\S?|EN\s*AMBAS\s*ZONAS|EN\s*EL\s*RESTO)\s*"
        r"(?:DE\s*LA|DEL)?\s*(?:TARDE|MANANA|DIA|MADRUGADA|MEDIODIA|NOCHE)?\s*(?:AREAS\s*DE|INTERVALOS\s*DE)?\s*"
        r"(?:VISIBILIDAD|RE?GULAR|BUENA|MALA|BRUMA|CALIMA|NIEBLA)",
    
    ]
    
    return claves

def claves_ordenar_fenomenos_temporalmente(valor, periodo, funcion):

    if periodo == 1:
        dic = {
            "TARDE": 2,
            "PRIMERAS HORAS DE LA TARDE": 1,
            "NOCHE": 3,
            "MEDIANOCHE": 4,
            "MADRUGADA": 5,
            r"FINAL\s*DE\s*LA\s*MADRUGADA": 6,
            r"AVANZADA\s*LA\s*MADRUGADA": 6,
            "MANANA DEL DIA": 7,
            "MANANA": 7,
            "MEDIODIA": 8,
            r"DIA \d+": 5,
            "DIA": 7,
        }

    elif periodo == 2:
        dic = {
            "NOCHE": 1,
            "MEDIANOCHE": 2,
            "MADRUGADA": 3,
            r"FINAL\s*DE\s*LA\s*MADRUGADA": 4,
            r"AVANZADA\s*LA\s*MADRUGADA": 4,
            "MANANA DEL DIA": 5,
            "MANANA": 5,
            "MEDIODIA": 6,
            "TARDE": 7,
            "PRIMERAS HORAS DE LA TARDE": 6,
            r"DIA \d+": 3,
            "DIA": 6,
    }
    if funcion == 1: #Traduccion
        return dic.get(valor, 'Desconocido')
    elif funcion == 2:
        return dic #Enumeracion

def claves_traducir(valor, fenomeno, variable, funcion):
    if fenomeno == 0:
        if variable == 1:
            clave = {
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORTE|N)\s?(O|Y|A|-)\s?(NOROESTE|NW)(?!\sDE\b)\b": 337.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NOROESTE|NW)\s?(O|Y|A|-)\s?(NORTE|N)(?!\sDE\b)\b": 337.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NOROESTE|NW)\s?(O|Y|A|-)\s?(OESTE|W)(?!\sDE\b)\b": 292.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(OESTE|W)\s?(O|Y|A|-)\s?(NOROESTE|NW)(?!\sDE\b)\b": 292.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(OESTE|W)\s?(O|Y|A|-)\s?(SUR?D?OESTE|SW)(?!\sDE\b)\b": 247.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?OESTE|SW)\s?(O|Y|A|-)\s?(OESTE|W)(?!\sDE\b)\b": 247.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?OESTE|SW)\s?(O|Y|A|-)\s?(SUR|S)(?!\sDE\b)\b": 202.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR|S)\s?(O|Y|A|-)\s?(SUR?D?OESTE|SW)(?!\sDE\b)\b": 202.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR|S)\s?(O|Y|A|-)\s?(SUR?D?ESTE|SE)(?!\sDE\b)\b": 157.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?ESTE|SE)\s?(O|Y|A|-)\s?(SUR|S)(?!\sDE\b)\b": 157.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?ESTE|SE)\s?(O|Y|A|-)\s?(ESTE|E)(?!\sDE\b)\b": 112.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(ESTE|E)\s?(O|Y|A|-)\s?(SUR?D?ESTE|SE)(?!\sDE\b)\b": 112.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(ESTE|E)\s?(O|Y|A|-)\s?(NORD?ESTE|NE)(?!\sDE\b)\b": 67.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORD?ESTE|NE)\s?(O|Y|A|-)\s?(ESTE|E)(?!\sDE\b)\b": 67.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORD?ESTE|NE)\s?(O|Y|A|-)\s?(NORTE|N)(?!\sDE\b)\b": 22.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORTE|N)\s?(O|Y|A|-)\s?(NORD?ESTE|NE)(?!\sDE\b)\b": 22.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NOROESTE|NW)(?!\sDE\b)\b": 315,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORD?ESTE|NE)(?!\sDE\b)\b": 45,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?OESTE|SW)(?!\sDE\b)\b": 225,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?ESTE|SE)(?!\sDE\b)\b": 135,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORTE|N|COMPONENTE\s?N)(?!\sDE\b)\b": 0,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR|S|COMPONENTE\s?S)(?!\sDE\b)\b": 180,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(OESTE|W|COMPONENTE\s?W)(?!\sDE\b)\b": 270,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(ESTE|E|COMPONENTE\s?E)(?!\sDE\b)\b": 90,
            }

        elif variable == 2:#MAXIMO
            clave = {
                r"1\s*(O|A)\s*2": 3.3,
                r"2\s*(O|A)\s*3": 5.4,
                r"3\s*(O|A)\s*4": 7.9,
                r"4\s*(O|A)\s*5": 10.7,
                r"5\s*(O|A)\s*6": 13.8,
                r"6\s*(O|A)\s*7": 17.1,
                r"7\s*(O|A|U)\s*8": 20.7,
                r"8\s*(O|A)\s*9": 24.4,
                r"1\s*A\s*3": 5.4,
                r"1\s*A\s*4": 7.9,
                r"2\s*A\s*4": 7.9,
                r"2\s*A\s*5": 10.7,
                r"3\s*A\s*5": 10.7,
                r"3\s*A\s*6": 13.8,
                r"4\s*A\s*6": 13.8,
                r"4\s*A\s*7": 17.1,
                r"5\s*A\s*7": 17.1,
                r"5\s*A\s*8": 20.7,
                r"6\s*A\s*8": 20.7,
                r"6\s*A\s*9": 24.4,
                r"7\s*A\s*9": 24.4,
                r"2\s*CON\s*INTERVALOS\s*DE\s*3": 5.4,
                r"3\s*CON\s*INTERVALOS\s*DE\s*4": 7.9,
                r"4\s*CON\s*INTERVALOS\s*DE\s*5": 10.7,
                r"5\s*CON\s*INTERVALOS\s*DE\s*6": 13.8,
                r"6\s*CON\s*INTERVALOS\s*DE\s*7": 17.1,
                r"7\s*CON\s*INTERVALOS\s*DE\s*8": 20.7,
                r"8\s*CON\s*INTERVALOS\s*DE\s*9": 24.4,
                r"2": 3.3,
                r"3": 5.4,
                r"4": 7.9,
                r"5": 10.7,
                r"6": 13.8,
                r"7": 17.1,
                r"8": 20.7,
                r"9": 24.4
            }
        elif variable == 3:#MEDIA
            clave = {
                r"1\s*(O|A)\s*2": 1.5,
                r"2\s*(O|A)\s*3": 3.3,
                r"3\s*(O|A)\s*4": 5.4,
                r"4\s*(O|A)\s*5": 7.9,
                r"5\s*(O|A)\s*6": 10.7,
                r"6\s*(O|A)\s*7": 13.8,
                r"7\s*(O|A|U)\s*8": 17.1,
                r"8\s*(O|A)\s*9": 20.7,
                r"1\s*A\s*3": 2.5,
                r"1\s*A\s*4": 3.45,
                r"2\s*A\s*4": 4.4,
                r"2\s*A\s*5": 5.55,
                r"3\s*A\s*5": 6.7,
                r"3\s*A\s*6": 8,
                r"4\s*A\s*6": 9.35,
                r"4\s*A\s*7": 10.8,
                r"5\s*A\s*7": 12.3,
                r"5\s*A\s*8": 13.9,
                r"6\s*A\s*8": 15.5,
                r"6\s*A\s*9": 17.225,
                r"7\s*A\s*9": 18.95,
                r"2\s*CON\s*INTERVALOS\s*DE\s*3": 3.3,
                r"3\s*CON\s*INTERVALOS\s*DE\s*4": 5.4,
                r"4\s*CON\s*INTERVALOS\s*DE\s*5": 7.9,
                r"5\s*CON\s*INTERVALOS\s*DE\s*6": 10.7,
                r"6\s*CON\s*INTERVALOS\s*DE\s*7": 13.8,
                r"7\s*CON\s*INTERVALOS\s*DE\s*8": 17.1,
                r"8\s*CON\s*INTERVALOS\s*DE\s*9": 20.7,
                r"2": 2.5,
                r"3": 4.4,
                r"4": 6.7,
                r"5": 9.35,
                r"6": 12.3,
                r"7": 15.5,
                r"8": 18.95,
                r"9": 22.6,
                "NO_CLAVE": "X"
            }
    
    elif fenomeno == 1:
        if variable == 1:
            clave = {}
        elif variable == 2:#MAXIMO
            clave = {
                r"(?:RIZADA\s?O\s?MA(?:RE{1,2})?JADILLA|MA(?:RE{1,2})?JADILLA\s?O\s?RIZADA)": 0.5,
                r"(?:MA(?:RE{1,2})?JADILLA\s?O\s?MA(?:RE{1,2})?JADA|MA(?:RE{1,2})?JADA\s?O\s?MA(?:RE{1,2})?JADILLA)": 1.25,
                r"(?:MA(?:RE{1,2})?JADA\s?O\s?FUERTE\s?MA(?:RE{1,2})?JADA|FUERTE\s?MA(?:RE{1,2})?JADA\s?O\s?MA(?:RE{1,2})?JADA)": 2.5,
                r"(?:FUERTE\s?MA(?:RE{1,2})?JADA\s?O\s?GRUESA|GRUESA\s?O\s?FUERTE\s?MA(?:RE{1,2})?JADA)": 4,
                r"(?:GRUESA\s?O\s?MUY\s?GRUESA|MUY\s?GRUESA\s?O\s?GRUESA)": 6,
                r"(?:MUY\s?GRUESA\s?O\s?ARBOLADA|ARBOLADA\s?O\s?MUY\s?GRUESA)": 9,
                r"(?:ARBOLADA\s?O\s?MONTANOSA|MONTANOSA\s?O\s?ARBOLADA)": 14,
                r"(?:MONTANOSA\s?O\s?ENORME|ENORME\s?O\s?MONTANOSA)": 16,
                r"RIZADA": 0.1,
                r"MA(?:RE{1,2})?JADILLA": 0.5,
                r"MA(?:RE{1,2})?JADA": 1.25,
                r"FUERTE\s?MA(?:RE{1,2})?JADA": 2.5,
                r"GRUESA": 4,
                r"MUY\s?GRUESA": 6,
                r"ARBOLADA": 9,
                r"MONTANOSA": 14,
                r"ENORME": 16
            }
        elif variable == 3:#MEDIA
            clave = {
                r"(?:RIZADA\s?O\s?MA(?:RE{1,2})?JADILLA|MA(?:RE{1,2})?JADILLA\s?O\s?RIZADA)": 0.25,
                r"(?:MA(?:RE{1,2})?JADILLA\s?O\s?MA(?:RE{1,2})?JADA|MA(?:RE{1,2})?JADA\s?O\s?MA(?:RE{1,2})?JADILLA)": 0.75,
                r"(?:MA(?:RE{1,2})?JADA\s?O\s?FUERTE\s?MA(?:RE{1,2})?JADA|FUERTE\s?MA(?:RE{1,2})?JADA\s?O\s?MA(?:RE{1,2})?JADA)": 1.75,
                r"(?:FUERTE\s?MA(?:RE{1,2})?JADA\s?O\s?GRUESA|GRUESA\s?O\s?FUERTE\s?MA(?:RE{1,2})?JADA)": 3.125,
                r"(?:GRUESA\s?O\s?MUY\s?GRUESA|MUY\s?GRUESA\s?O\s?GRUESA)": 5,
                r"(?:MUY\s?GRUESA\s?O\s?ARBOLADA|ARBOLADA\s?O\s?MUY\s?GRUESA)": 7.5,
                r"(?:ARBOLADA\s?O\s?MONTANOSA|MONTANOSA\s?O\s?ARBOLADA)": 11.5,
                r"(?:MONTANOSA\s?O\s?ENORME|ENORME\s?O\s?MONTANOSA)": 15,
                r"RIZADA": 0.1,
                r"MA(?:RE{1,2})?JADILLA": 0.25,
                r"FUERTE\s?MA(?:RE{1,2})?JADA": 1.75,
                r"MA(?:RE{1,2})?JADA": 0.75,
                r"MUY\s?GRUESA": 5,
                r"GRUESA": 3.125,
                r"ARBOLADA": 7.5,
                r"MONTANOSA": 11.5,
                r"ENORME": 15,
            }
            
    elif fenomeno == 2:
        if variable == 1:
            clave = {
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORTE|N)\s?(O|Y|A|-)\s?(NOROESTE|NW)\b": 337.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NOROESTE|NW)\s?(O|Y|A|-)\s?(NORTE|N)\b": 337.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NOROESTE|NW)\s?(O|Y|A|-)\s?(OESTE|W)\b": 292.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(OESTE|W)\s?(O|Y|A|-)\s?(NOROESTE|NW)\b": 292.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(OESTE|W)\s?(O|Y|A|-)\s?(SUR?D?OESTE|SW)\b": 247.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?OESTE|SW)\s?(O|Y|A|-)\s?(OESTE|W)\b": 247.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?OESTE|SW)\s?(O|Y|A|-)\s?(SUR|S)\b": 202.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR|S)\s?(O|Y|A|-)\s?(SUR?D?OESTE|SW)\b": 202.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR|S)\s?(O|Y|A|-)\s?(SUR?D?ESTE|SE)\b": 157.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?ESTE|SE)\s?(O|Y|A|-)\s?(SUR|S)\b": 157.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?ESTE|SE)\s?(O|Y|A|-)\s?(ESTE|E)\b": 112.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(ESTE|E)\s?(O|Y|A|-)\s?(SUR?D?ESTE|SE)\b": 112.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(ESTE|E)\s?(O|Y|A|-)\s?(NORD?ESTE|NE)\b": 67.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORD?ESTE|NE)\s?(O|Y|A|-)\s?(ESTE|E)\b": 67.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORD?ESTE|NE)\s?(O|Y|A|-)\s?(NORTE|N)\b": 22.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORTE|N)\s?(O|Y|A|-)\s?(NORD?ESTE|NE)\b": 22.5,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NOROESTE|NW)\b": 315,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORD?ESTE|NE)\b": 45,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?OESTE|SW)\b": 225,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR?D?ESTE|SE)\b": 135,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(NORTE|N|COMPONENTE\s?N)\b": 0,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(SUR|S|COMPONENTE\s?S)\b": 180,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(OESTE|W|COMPONENTE\s?W)\b": 270,
                r"(?<!EN EL\s)(?<!EXTREMO\s)\b(ESTE|E|COMPONENTE\s?E)\b": 90,
            }
        elif variable == 2:#MAXIMO
            clave = {
                r"1\s*(A|O|Y)\s*2": 2,
                r"2\s*(A|O|Y)\s*3": 3,
                r"3\s*(A|O|Y)\s*4": 4,
                r"4\s*(A|O|Y)\s*5": 5,
                r"5\s*(A|O|Y)\s*6": 6,
                r"6\s*(A|O|Y)\s*7": 7,
                r"7\s*(A|O|Y|U)\s*8": 8,
                r"8\s*(A|O|Y)\s*9": 9,
                r"1\s*A\s*3": 3,
                r"2\s*A\s*4": 4,
                r"3\s*A\s*5": 5,
                r"4\s*A\s*6": 6,
                r"5\s*A\s*7": 7,
                r"6\s*A\s*8": 8,
                r"7\s*A\s*9": 9,
                r"1\s*A\s*4": 4,
                r"2\s*A\s*5": 5,
                r"3\s*A\s*6": 6,
                r"4\s*A\s*7": 7,
                r"5\s*A\s*8": 8,
                r"6\s*A\s*9": 9,
                r"1\s*(METRO|m)": 1.25,
                r"2\s*(METRO|m)": 2.25,
                r"3\s*(METRO|m)": 3.25,
                r"4\s*(METRO|m)": 4.25,
                r"5\s*(METRO|m)": 5.25,
                r"6\s*(METRO|m)": 6.25,
                r"7\s*(METRO|m)": 7.25,
                r"8\s*(METRO|m)": 8.25,
                "NO_CLAVE":1
            }
        elif variable == 3:#MEDIA
            clave = {
                r"1\s*(A|O|Y)\s*2": 1.5,
                r"2\s*(A|O|Y)\s*3": 2.5,
                r"3\s*(A|O|Y)\s*4": 3.5,
                r"4\s*(A|O|Y)\s*5": 4.5,
                r"5\s*(A|O|Y)\s*6": 5.5,
                r"6\s*(A|O|Y)\s*7": 6.5,
                r"7\s*(A|O|Y|U)\s*8": 7.5,
                r"8\s*(A|O|Y)\s*9": 8.5,
                r"1\s*A\s*3": 2,
                r"2\s*A\s*4": 3,
                r"3\s*A\s*5": 4,
                r"4\s*A\s*6": 5,
                r"5\s*A\s*7": 6,
                r"6\s*A\s*8": 7,
                r"7\s*A\s*9": 8,
                r"1\s*A\s*4": 2.5,
                r"2\s*A\s*5": 3.5,
                r"3\s*A\s*6": 4.5,
                r"4\s*A\s*7": 5.5,
                r"5\s*A\s*8": 6.5,
                r"6\s*A\s*9": 7.5,
                r"1\s*(METRO|m)": 1,
                r"2\s*(METRO|m)": 2,
                r"3\s*(METRO|m)": 3,
                r"4\s*(METRO|m)": 4,
                r"5\s*(METRO|m)": 5,
                r"6\s*(METRO|m)": 6,
                r"7\s*(METRO|m)": 7,
                r"8\s*(METRO|m)": 8,
                "NO_CLAVE": 0.5
            }

    elif fenomeno == 3:
        if variable == 1:
            clave = {}
        elif variable == 2:
            clave = {}
        elif variable == 3:
            clave = {}
    elif fenomeno == 4:
        if variable == 1:
            clave = {}
        elif variable == 2:
            clave = {}
        elif variable == 3:
            clave = {}

    if funcion == 1: #Traduccion
        return clave.get(valor)
    elif funcion == 2:
        return clave #Enumeracion

def generar_lineas(seccion, fecha, div_por_zona, dic_divisiones, i):

    boletin_recortado = ""
    seccion = re.sub(r'^(.*?):', '', seccion)# Eliminar aguas costeras y el nombre de la región en el encabezado de cada sección
    
    seccion = re.sub(r'(?<!\.)\n', '', seccion) # Eliminar saltos de línea donde no hay punto final

    if div_por_zona[i] != 1:
        claves_saltos = claves_generar_lineas()
        union_claves_saltos = '|'.join(claves_saltos)
        # Genera saltos tras un - o ; interpretable como comienzo de linea
        seccion = re.sub(fr'({union_claves_saltos})', r'\n\1', seccion, flags=re.IGNORECASE) 
        
    seccion = re.sub(r';', '.', seccion) # Cambia los ';' por '.'

    seccion = re.sub(r'(\.)(?!\s*$)', r'\1\n', seccion) # Añadir salto de línea después de cada punto y eliminar espacio al principio de la línea siguiente
    
    seccion = re.sub(r'^\s+', '', seccion, flags=re.MULTILINE) # Eliminar espacios al principio de cada línea

    boletin_recortado = f"{seccion}"# Formatear la sección con el identificador de zona y contenido modificado
    
    return boletin_recortado, seccion

def escribir_lineas(separar_por_zonas, n, fenomenos_separar_por_zonas, procesar_fenomeno_por_zonas, sustituir_zona, per_zona, dic_boletin, div_por_zona, divisor, other, k, m):#subfuncion de ordenar lineas

    if separar_por_zonas == True and (n==1 or (fenomenos_separar_por_zonas[0] <= m <= fenomenos_separar_por_zonas[1])):    
        if not any(per_zona):
            for l in range(div_por_zona):
                procesar_fenomeno_por_zonas[l] = False
                if divisor: 
                    dic_boletin[k + l][m].append(divisor + other)
                else:
                    dic_boletin[k + l][m].append(other)
        
        else:
            for l in range(div_por_zona):
                if per_zona[l]:
                    procesar_fenomeno_por_zonas[l] = False
                    if divisor: 
                        dic_boletin[k + l][m].append(divisor + other)
                    else:
                        dic_boletin[k + l][m].append(other)

    elif sustituir_zona == True:
        if not any(per_zona):
            for l in range(div_por_zona):
                procesar_fenomeno_por_zonas[l] = False
                if divisor:
                    dic_boletin[k + l][m] = [divisor + other]  
                else:
                    dic_boletin[k + l][m] = [other]
        
        else:
            for l in range(div_por_zona):
                if per_zona[l]:
                    procesar_fenomeno_por_zonas[l] = False
                    if divisor:
                        dic_boletin[k + l][m] = [divisor + other]  
                    else:
                        dic_boletin[k + l][m] = [other]
            
    else:
        for l in range(div_por_zona):
            if divisor: 
                dic_boletin[k + l][m].append(divisor + other)
            else:
                dic_boletin[k + l][m].append(other)
        
    return dic_boletin, procesar_fenomeno_por_zonas

def ordenar_lineas(seccion, fecha, cod_boletin, div_por_zona, dic_divisiones, num_zonas, num_divisiones): #separa el boletin por zonas (solo viento y mar de viento) y por tipo de fenomeno
    
    dic_boletin = {i: {j: [] for j in range(5)} for i in range(num_divisiones)}
        
    claves = {i: [] for i in range(5)}

    lineas = []
    
    for i in range(5):
        claves[i] = claves_ordenar_lineas_por_tipo_fenomeno(i)

    claves_meteoros = {}
    claves_meteoros = claves[3] + claves[4]

    procesar_fenomeno_por_zonas = [[True for _ in range(num_divisiones)] for _ in range(5)] 
    k = 0
    
    for j in range(num_zonas):

        separar_por_zonas = False
        per_zona = [False] * div_por_zona[j]
        resto_zona = [True] * div_por_zona[j]
        fenomenos_separar_por_zonas = [-1, -1]
        
        lineas = seccion[j].split('\n')

        if div_por_zona[j] == 1:
            for i in range(5):
                procesar_fenomeno_por_zonas[i][k]=False
        
        elif div_por_zona[j] != 1:

            claves_zona = [[] for _ in range(div_por_zona[j])]
            claves_principio_zona = [[] for _ in range(div_por_zona[j])]
            
            lista_claves_zona = [[] for _ in range(div_por_zona[j])]
            lista_claves_principio_zona = [[] for _ in range(div_por_zona[j])]
      
            union_claves_zona = ""
            union_claves_principio_zona = ""
            
            for l in range(div_por_zona[j]):
                lista_claves_zona[l] = claves_ordenar_por_zonas(cod_boletin, j, dic_divisiones[j][l], div_por_zona[j], 1)
                claves_zona[l] = ('|'.join(lista_claves_zona[l]) + '|').rstrip('|')
                union_claves_zona += '|'.join(lista_claves_zona[l]) + '|'
                
                lista_claves_principio_zona[l] = [r'^' + clave for clave in lista_claves_zona[l]]
                claves_principio_zona[l] = ('|'.join(lista_claves_principio_zona[l]) + '|').rstrip('|')
                union_claves_principio_zona += '|'.join(lista_claves_principio_zona[l]) + '|'    

            union_claves_zona = union_claves_zona.rstrip('|')
            union_claves_principio_zona = union_claves_principio_zona.rstrip('|')

            claves_principio_no_zona = claves_ordenar_por_zonas(cod_boletin, j, "no_zona", div_por_zona[j], 1)
            union_claves_no_zona = '|'.join(claves_principio_no_zona) 
            claves_principio_no_zona = [r'^' + clave for clave in claves_principio_no_zona]
            union_claves_principio_no_zona = '|'.join(claves_principio_no_zona) 
           
            claves_principio_resto = claves_ordenar_por_zonas(cod_boletin, j, "resto", div_por_zona[j], 1)
            union_claves_resto = '|'.join(claves_principio_resto)
            claves_principio_resto = [r'^' + clave for clave in claves_principio_resto]
            union_claves_principio_resto = '|'.join(claves_principio_resto)

            union_claves_principio = f"{union_claves_principio_zona}|{union_claves_principio_no_zona}|{union_claves_principio_resto}"
            union_claves = f"{union_claves_zona}|{union_claves_no_zona}|{union_claves_resto}"

            union_claves_principio = union_claves_principio.rstrip('|')
            union_claves = union_claves.rstrip('|')

            p = 0
            
            for linea in lineas:
                if re.search(union_claves_principio, linea, re.IGNORECASE):
                    p += 1

            if p == 1:
                for idx, linea in enumerate(lineas):
                    x = None
                    primera_coincidencia = None

                    for l in range(div_por_zona[j]):
                        if re.search(claves_principio_zona[l], linea, re.IGNORECASE):
                            primera_coincidencia = re.search(claves_principio_zona[l], linea, re.IGNORECASE)
                            x = l  
                            break
                    
                    if primera_coincidencia is not None:
                        for l in range(div_por_zona[j]):
                            if l != x:
                                segunda_coincidencia = re.search(claves_zona[l], linea[primera_coincidencia.end():], re.IGNORECASE)
                                if segunda_coincidencia:
                                    break

                        if segunda_coincidencia is None:
                            segunda_coincidencia = re.search(union_claves_resto, linea[primera_coincidencia.end():], re.IGNORECASE)

                        if segunda_coincidencia is None:
                            segunda_coincidencia = re.search(union_claves_no_zona, linea[primera_coincidencia.end():], re.IGNORECASE)

                        if segunda_coincidencia:
                            separar_por_zonas = True
                            pos_segunda = primera_coincidencia.end() + segunda_coincidencia.start()
                            primera_parte = linea[:pos_segunda].strip()
                            segunda_parte = linea[pos_segunda:].strip()

                            lineas[idx] = primera_parte
                            lineas.insert(idx + 1, segunda_parte)
                            break

            elif p >= 2:
                separar_por_zonas = True
                lineas = [linea.strip() for linea in lineas]
        # print(p)
        n=0
        
        fenomenos_separar_por_zonas0 = False
          
        for linea in lineas:
    
            primer_fen = False
            divisor = None
            sustituir_zona = False

            if div_por_zona[j] != 1 and separar_por_zonas == False and re.search(union_claves_principio_zona, linea, re.IGNORECASE):
                sustituir_zona = True

            if fenomenos_separar_por_zonas0 == True:
                fenomenos_separar_por_zonas[0] = m 
                fenomenos_separar_por_zonas0 = False

            if separar_por_zonas == True:
                if re.search(union_claves_principio_zona, linea, re.IGNORECASE) or re.search(union_claves_principio_resto, linea, re.IGNORECASE):
                    per_zona = [False] * div_por_zona[j]
                    
                    if n == 0:
                        fenomenos_separar_por_zonas0 = True           
                    if n == 1:
                        fenomenos_separar_por_zonas[1] = m
                    n += 1

                    if re.search(union_claves_principio_resto, linea, re.IGNORECASE):
                        per_zona = resto_zona
                    else:
                        for l in range(div_por_zona[j]):
                            for clave in lista_claves_principio_zona[l]:
                                if re.search(clave, linea, re.IGNORECASE):
                                    per_zona[l] = True
                                    resto_zona[l] = False

                elif re.search(union_claves_principio_no_zona, linea, re.IGNORECASE):                            
                    per_zona = [False] * div_por_zona[j]
                
            elif sustituir_zona == True:
                for l in range(div_por_zona[j]):
                    for clave in lista_claves_principio_zona[l]:
                        if re.search(clave, linea, re.IGNORECASE):
                            per_zona[l] = True
                            resto_zona[l] = False
            
            m = -1 #Quitar para completar patrones

            claves_meteoros = sorted(claves_meteoros, key=lambda orden: ordenar_claves_segun_linea(orden, linea))
            
            if claves_meteoros[0] in claves[4]:
                indices_met = [4,3]
            else:
                indices_met = [3,4] 

            indices = list(range(0, 3)) + indices_met

            for i in indices:

                claves[i] = sorted(claves[i], key=lambda orden: ordenar_claves_segun_linea(orden, linea))

                if re.search(claves[i][0], linea, re.IGNORECASE):  
                    partes = re.split(f'({claves[i][0]})', linea, 1, flags=re.IGNORECASE)
                    # print(linea, claves[i][0])  
                    # print(partes)
                    if primer_fen:
                        linea = partes[2]
                        other = partes[0]

                        dic_boletin, procesar_fenomeno_por_zonas[m] = escribir_lineas(separar_por_zonas, n, fenomenos_separar_por_zonas, procesar_fenomeno_por_zonas[m], sustituir_zona, per_zona, dic_boletin, div_por_zona[j], divisor, other, k, m)

                        divisor = partes[1]

                    primer_fen = True
                    m=i
            
            if m != -1: #Quitar para completar patrones

                dic_boletin, procesar_fenomeno_por_zonas[m] = escribir_lineas(separar_por_zonas, n, fenomenos_separar_por_zonas, procesar_fenomeno_por_zonas[m], sustituir_zona, per_zona, dic_boletin, div_por_zona[j], divisor, linea, k, m)
            # else:
            #     if linea != "":
            #         print(linea, fecha) 
        k += div_por_zona[j]  
        
    return dic_boletin, procesar_fenomeno_por_zonas

def separar_lineas_temporalmente(dic_boletin, fecha): #separa cada fenomeno en cachos temporales temporalmente,
    
    temp_boletin = {i: [] for i in range(5)}
    
    divisores_ord = claves_separar_lineas_temporalmente()
    
    for i in range(5):
        for fenomeno in dic_boletin[i]:
            divisor = None
            j=0

            while j < len(divisores_ord):
                if j == 0:
                    divisores_ord = sorted(divisores_ord, key=lambda orden: ordenar_claves_segun_linea(orden, fenomeno))
                    # print(f"Fenómeno: {fenomeno}, Primer divisor: {divisores_ord[0]}")

                match = re.search(divisores_ord[j], fenomeno, re.IGNORECASE)
                if match:
                    partes = re.split(f'({divisores_ord[j]})', fenomeno, 1, flags=re.IGNORECASE)
                    if len(partes) < 3:  # Verificación de seguridad
                        # print(f"Patrón '{divisores_ord[j]}' no produjo una división válida")
                        j += 1
                        continue
                    
                    other = partes[0]
                    if other:
                        if divisor:
                            temp_boletin[i].append(divisor + other)
                        else:
                            temp_boletin[i].append(other)
                    
                    divisor = partes[1]
                    fenomeno = partes[2]
                    # print(f"Fenómeno restante: {fenomeno}")
                    
                    j = 0
                else:
                    j += 1

            if divisor:    
                temp_boletin[i].append(divisor + fenomeno)
            else:
                if fenomeno != "":
                    temp_boletin[i].append(fenomeno)
            
    return temp_boletin

def ordenar_fenomenos_por_zonas(boletin_sep_fen, procesar_fenomeno_por_zonas, cod_boletin, div_por_zona, dic_divisiones, num_zonas, num_divisiones):#En el caso en que el boletin NO separe por zonas, separa fenomenos locales

    boletin_sep_zona = {}
    
    for j in range(num_divisiones):
        boletin_sep_zona[j] = {i: [] for i in range(5)}

    k = 0
    
    for j in range(num_zonas):
        
        if div_por_zona[j] != 1:
            claves_zona = [[] for _ in range(div_por_zona[j])]
            union_claves_zona = ""
            
            for l in range(div_por_zona[j]):
                claves_zona[l] = claves_ordenar_por_zonas(cod_boletin, j, dic_divisiones[j][l], div_por_zona[j], 2)
                union_claves_zona += '|'.join(claves_zona[l]) + '|'
            union_claves_zona = union_claves_zona.rstrip('|')
            
            claves_no_zona = claves_ordenar_por_zonas(cod_boletin, j, "no_zona", div_por_zona[j], 2)
            union_claves_no_zona = '|'.join(claves_no_zona) 
           
            claves_resto = claves_ordenar_por_zonas(cod_boletin, j, "resto", div_por_zona[j], 2)
            union_claves_resto = '|'.join(claves_resto)
             
        for i in range(5):

            for l in range(div_por_zona[j]):
                if not procesar_fenomeno_por_zonas[i][k + l]:
                    boletin_sep_zona[k + l][i] = boletin_sep_fen[k + l][i]
                else:
                    m=l
            
            if any(procesar_fenomeno_por_zonas[i][k + l] for l in range(div_por_zona[j])):
                                
                resto_zona = [True] * div_por_zona[j]
                                
                for fenomeno in boletin_sep_fen[k + m][i]:

                    per_zona = [False] * div_por_zona[j]
                    
                    if re.search(union_claves_resto, fenomeno, re.IGNORECASE):
                        per_zona = resto_zona
                    elif re.search(union_claves_no_zona, fenomeno, re.IGNORECASE):                            
                        per_zona = [False] * div_por_zona[j]
                    else:
                        for l in range(div_por_zona[j]):
                            for clave in claves_zona[l]:
                                if re.search(clave, fenomeno, re.IGNORECASE):
                                    per_zona[l] = True
                                    resto_zona[l] = False

                    if not any(per_zona):
                        for l in range(div_por_zona[j]):
                            if procesar_fenomeno_por_zonas[i][k + l]:
                                boletin_sep_zona[k + l][i].append(fenomeno)

                    else:
                        for l in range(div_por_zona[j]):
                            if per_zona[l] and procesar_fenomeno_por_zonas[i][k + l]:
                                boletin_sep_zona[k + l][i].append(fenomeno)
                                
        k += div_por_zona[j]

    return boletin_sep_zona

def ordenar_fenomenos_temporalmente(temp_boletin, periodo):#coloca cada fenomeno en el tiempo correcto

    claves_trad_temp = claves_ordenar_fenomenos_temporalmente(None, periodo, 2)

    claves_temp = '|'.join(claves_trad_temp)
    
    boletin_sep_temp = {}

    step = None
    step_anterior = None

    for j in range(0, 9):
        boletin_sep_temp[j] = {i: [] for i in range(5)}

    for i in range(5):
        primer_fen=True
        for fenomeno in temp_boletin[i]:
            # print(fenomeno)
            if primer_fen:
                for j in range(0, 9):
                    boletin_sep_temp[j][i].append(fenomeno)
                if step is not None:
                    step_anterior = step
                step=int(0)       
                primer_fen=False
            else:  
                if re.search(r'(COMBINADA|SIGNIFICATIVA)', fenomeno, re.IGNORECASE) and i == 2:
                    continue
                elif re.search('DURANTE', fenomeno, re.IGNORECASE):#1 STEP ALANTE DEL FENOMENO, SOLO ESOS
                    for clave in claves_trad_temp: 
                        primer_temp=False
                        if re.search(clave, fenomeno, re.IGNORECASE):
                            primer_temp=True
                            step=int(claves_ordenar_fenomenos_temporalmente(clave, periodo, 1))
                            start_step = max(step - 1, 0)  
                            end_step = min(step + 1, 8)
                            partes = re.split(clave, fenomeno, re.IGNORECASE)
                            fenomeno2 = partes[1]
                            segundo_temp=False
                            for clave2 in claves_trad_temp: 
                                if re.search(clave2, fenomeno2, re.IGNORECASE):
                                    step2=int(claves_ordenar_fenomenos_temporalmente(clave2, periodo, 1))
                                    end_step = min(step2 + 1, 8)
                                    for j in range(start_step, end_step):
                                        boletin_sep_temp[j][i] = []
                                        boletin_sep_temp[j][i].append(fenomeno)
                                    segundo_temp=True
                                    break    
                            if not segundo_temp: 
                                for j in range(start_step, end_step):
                                    boletin_sep_temp[j][i] = []
                                    boletin_sep_temp[j][i].append(fenomeno)
                            step=end_step
                            break
                
                elif re.search(r'A\s*PARTIR', fenomeno, re.IGNORECASE) or re.search(r'POR\s*EL', fenomeno, re.IGNORECASE) or re.search(r'POR\s*LA', fenomeno, re.IGNORECASE):#DESDE ESTE HASTA EL FINAL
                    for clave in claves_trad_temp:    
                        if re.search(clave, fenomeno, re.IGNORECASE):
                            step=int(claves_ordenar_fenomenos_temporalmente(clave, periodo, 1))
                            for j in range(step, 9):
                                boletin_sep_temp[j][i] = []
                                boletin_sep_temp[j][i].append(fenomeno)
                            break
                
                elif re.search('HASTA', fenomeno, re.IGNORECASE):#DEL ANTERIOR PUNTO A ESTE
                    for clave in claves_trad_temp:    
                        if re.search(clave, fenomeno, re.IGNORECASE):
                            step2=int(claves_ordenar_fenomenos_temporalmente(clave, periodo, 1))
                            for j in range(step, step2):
                                boletin_sep_temp[j][i].append(fenomeno)
                            step=step2
                            break

                elif re.search('HOY', fenomeno, re.IGNORECASE):#DEL ANTERIOR PUNTO A ESTE
                    step2=int(claves_ordenar_fenomenos_temporalmente("MEDIANOCHE", periodo, 1))
                    for j in range(step, step2):
                        boletin_sep_temp[j][i].append(fenomeno)
                    step=step2
            
                elif (re.search('ENTRE', fenomeno, re.IGNORECASE) or 
                      (re.search('DESDE', fenomeno, re.IGNORECASE) and not re.search(r"EL\s*NORTE|EL\s*NORESTE|EL\s*NOROESTE|EL\s*SUR|EL\s*SURESTE|EL\s*SUROESTE|EL\s*OESTE|EL\s*ESTE", fenomeno, re.IGNORECASE))):#Buscar 2 claves y escribirlo entre ellas
                    for clave in claves_trad_temp:    
                        primer_temp=False
                        if re.search(clave, fenomeno, re.IGNORECASE):
                            primer_temp=True
                            step=int(claves_ordenar_fenomenos_temporalmente(clave, periodo, 1))
                            partes = re.split(clave, fenomeno, re.IGNORECASE)
                            fenomeno2 = partes[1]
                            segundo_temp=False
                            for clave2 in claves_trad_temp: 
                                if re.search(clave2, fenomeno2, re.IGNORECASE):
                                    step2=int(claves_ordenar_fenomenos_temporalmente(clave2, periodo, 1))
                                    for j in range(step, step2):
                                        boletin_sep_temp[j][i] = []
                                        boletin_sep_temp[j][i].append(fenomeno)
                                    segundo_temp=True
                                    break    
                            if not segundo_temp:
                                for j in range(step, 9):
                                    boletin_sep_temp[j][i] = []
                                    boletin_sep_temp[j][i].append(fenomeno)
                            break
                    if not primer_temp:
                        for j in range(step, 9):
                            boletin_sep_temp[j][i].append(fenomeno) 
                
                elif re.search('MAS TARDE', fenomeno, re.IGNORECASE) or re.search('RAPIDAMENTE', fenomeno, re.IGNORECASE) or re.search('PRONTO', fenomeno, re.IGNORECASE):#CUBRIR DESDE EL ULTIMO STEP HASTA EL FINAL; SERA EL POR DEFECTO
                    for j in range(step + 1, 9):
                        boletin_sep_temp[j][i] = []
                        boletin_sep_temp[j][i].append(fenomeno) 

                elif re.search(r'AL\s*PRINCIPIO\s*Y\s*(?:AL)?\s*FINAL', fenomeno, re.IGNORECASE) and not re.search(claves_temp, fenomeno, re.IGNORECASE):
                    boletin_sep_temp[0][i] = []
                    boletin_sep_temp[0][i].insert(0, fenomeno)
                    boletin_sep_temp[8][i] = []
                    boletin_sep_temp[8][i].insert(0, fenomeno) 
                
                elif re.search(r'AL\s*PRINCIPIO', fenomeno, re.IGNORECASE) and not re.search(claves_temp, fenomeno, re.IGNORECASE):
                    boletin_sep_temp[0][i] = []
                    boletin_sep_temp[0][i].insert(0, fenomeno)   

                elif re.search(r'AL\s*FINAL', fenomeno, re.IGNORECASE) and not re.search(claves_temp, fenomeno, re.IGNORECASE):
                    boletin_sep_temp[8][i] = []
                    boletin_sep_temp[8][i].insert(0, fenomeno) 

                else:
                    clave_sin=False
                    for clave in claves_trad_temp: 
                        if re.search(clave, fenomeno, re.IGNORECASE):
                            step=int(claves_ordenar_fenomenos_temporalmente(clave, periodo, 1))
                            clave_sin=True
                            for j in range(step, 9):
                                boletin_sep_temp[j][i] = []
                                boletin_sep_temp[j][i].append(fenomeno)
                            break   
                    if not clave_sin:
                        if i == 1 and step_anterior is not None and step_anterior != step and (re.search('AUMENTANDO', fenomeno, re.IGNORECASE) or re.search('DISMINUYENDO', fenomeno, re.IGNORECASE)):
                            for j in range(step_anterior, 9):
                                boletin_sep_temp[j][i] = []
                                boletin_sep_temp[j][i].append(fenomeno)
                        else:
                            for j in range(step, 9):
                                boletin_sep_temp[j][i].append(fenomeno)
            primer_fen=False

    return boletin_sep_temp

def traducir(dic_boletin):#busca las palabras clave de traduccion y las cambia por la traduccion de la funcion superior
    
    dat_boletin={}

    for j in range(0, 9):
        dat_boletin[j] = {i: [] for i in range(25)} 
    
    for i in range(5):

        for j in range (0,9):
            
            claves_trad_1 = claves_traducir(None, i, 1, 2)
            claves_trad_2 = claves_traducir(None, i, 2, 2)
            claves_trad_3 = claves_traducir(None, i, 3, 2)
            
            for fenomeno in dic_boletin[j][i]:
                
                for clave in claves_trad_1:  
                    if re.search(clave, fenomeno, re.IGNORECASE):  # Buscar si la clave está en el fenómeno
                        try:
                            valor_numerico = float(claves_traducir(clave, i, 1, 1))  
                            sin_dat = math.sin(math.radians(valor_numerico))  
                            cos_dat = math.cos(math.radians(valor_numerico))  
                        except ValueError:
                            valor_numerico = None
                            sin_dat = None
                            cos_dat = None
                        except KeyError:
                            valor_numerico = None
                            sin_dat = None
                            cos_dat = None

                        dat_boletin[j][i * 5].append(valor_numerico)
                        dat_boletin[j][i * 5 + 1].append(sin_dat)
                        dat_boletin[j][i * 5 + 2].append(cos_dat)
                        break #Quitar hacer que pasen todos los fenomenos
                                        
                for clave in claves_trad_2:  
                    if re.search(clave, fenomeno, re.IGNORECASE):
                        dat_boletin[j][i * 5 + 3].append(claves_traducir(clave, i, 2, 1))
                        break
            
                for clave in claves_trad_3:    
                    if re.search(clave, fenomeno, re.IGNORECASE):
                        dat_boletin[j][i * 5 + 4].append(claves_traducir(clave, i, 3, 1))
                        break
                
            if dat_boletin[j][i * 5] == []:
                dat_boletin[j][i * 5].append(claves_traducir("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 + 1] == []:
                dat_boletin[j][i*5 + 1].append(claves_traducir("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 + 2] == []:
                dat_boletin[j][i*5 + 2].append(claves_traducir("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 + 3] == []:
                dat_boletin[j][i*5 + 3].append(claves_traducir("NO_CLAVE", i, 2, 1))
            if dat_boletin[j][i*5 + 4] == []:
                dat_boletin[j][i*5 + 4].append(claves_traducir("NO_CLAVE", i, 3, 1))

    return dat_boletin

def reducir_unico_valor_por_campo(dat_boletin, div_por_zona, num_zonas, num_divisiones):#selecciona un unico valor dentro de cada intervalo temporal
    
    dat_final={}
    
    dat_final = {k: {j: {i: [] for i in range(25)} for j in range(9)} for k in range(num_divisiones)}
    
    k = 0
    
    for k in range(num_divisiones): 
        for j in range (0,9):
            for i in range(5):
        
                valores_numericos = []
                for valor in dat_boletin[k][j][5*i+1]:
                    if valor is not None:
                        try:
                            numero = float(valor)
                            valores_numericos.append(numero)
                        except ValueError:
                            continue
                if valores_numericos:
                    suma_valores=sum(valores_numericos)
                    media = suma_valores / len(valores_numericos)
                    dat_final[k][j][5*i+1] = media
                else:
                    dat_final[k][j][5*i+1] = None

                valores_numericos = []
                for valor in dat_boletin[k][j][5*i+2]:
                    if valor is not None:
                        try:
                            numero = float(valor)
                            valores_numericos.append(numero)
                        except ValueError:
                            continue
                if valores_numericos:
                    suma_valores=sum(valores_numericos)
                    media = suma_valores / len(valores_numericos)
                    dat_final[k][j][5*i+2] = media
                else:
                    dat_final[k][j][5*i+2] = None

                if dat_final[k][j][5*i+2] is not None and dat_final[k][j][5*i+1] is not None:
                    cuad = sqrt(dat_final[k][j][5*i+2]**2 + dat_final[k][j][5*i+1]**2)
                    if cuad != 0:
                        dat_final[k][j][5*i+1] = dat_final[k][j][5*i+1] / cuad
                        dat_final[k][j][5*i+2] = dat_final[k][j][5*i+2] / cuad
                    dat_final[k][j][5*i] = degrees(atan2(dat_final[k][j][5*i+1], dat_final[k][j][5*i+2]))
                    if dat_final[k][j][5*i] < 0:
                        dat_final[k][j][5*i] +=360
                else:
                    dat_final[k][j][5*i] = None
                

                valores_numericos = []
                for valor in dat_boletin[k][j][5*i+3]:
                    if valor is not None:  
                        try:
                            numero = float(valor)
                            valores_numericos.append(numero)
                        except ValueError:
                            continue
                if valores_numericos:
                    valor_maximo = max(valores_numericos) 
                    dat_final[k][j][5*i+3] = valor_maximo
                else:
                    dat_final[k][j][5*i+3] = None

            
                valores_numericos = []
                for valor in dat_boletin[k][j][5*i+4]: 
                    if valor is not None:  
                        try:
                            numero = float(valor)
                            valores_numericos.append(numero)
                        except ValueError:
                            continue
                if valores_numericos:
                    suma_valores=sum(valores_numericos)
                    media = suma_valores / len(valores_numericos)
                    dat_final[k][j][5*i+4] = media
                else:
                    dat_final[k][j][5*i+4] = None

    #Copia valores en instantes posteriores
    
    for k in range(num_divisiones): 
        for i in range(5):
            for j in range(1, 9): 
                for n in range(5):  
                    if dat_final[k][j][i * 5 + n] is None:
                        dat_final[k][j][i * 5 + n] = dat_final[k][j - 1][i * 5 + n]

    #Copia valores entre zonas de la misma division    
                
    k=0
    for m in range(num_zonas):
        for j in range(9):
            for i in range(5):
                for n in range(5): 
                    # Recopilar valores por división en la misma posición
                    valores_por_division = [dat_final[k + l][j][i * 5 + n] for l in range(div_por_zona[m])]
                    
                    # Verificar el contenido de valores_por_division en cada iteración
                    # print(f"Valores por división en (j={j}, i={i}, n={n}): {valores_por_division}")
                    
                    # Verificar si solo un valor es no nulo
                    if sum(v is not None for v in valores_por_division) == 1:
                        valor_no_nulo = next(v for v in valores_por_division if v is not None)
                        
                        # Propagar el valor no nulo a las posiciones nulas
                        for l in range(div_por_zona[m]):
                            if dat_final[k + l][j][i * 5 + n] is None:
                                dat_final[k + l][j][i * 5 + n] = valor_no_nulo
                                # print(f"Propagado valor {valor_no_nulo} en posición (k + l={k + l}, j={j}, i * 5 + n={i * 5 + n})")
        k+=div_por_zona[m]

    #Copia valores en instantes posteriores

    # for k in range(num_divisiones): 
    #     for i in range(5):
    #         for j in range(7, -1, -1): 
    #             for n in range(5):  
    #                 if dat_final[k][j][i * 5 + n] is None:
    #                     dat_final[k][j][i * 5 + n] = dat_final[k][j + 1][i * 5 + n]

    return dat_final

def convertir_csv(dat_final, ruta_csv, fecha, periodo, nombre_zona, nombre_division, i):

    if nombre_division[i] != 0:
            nombre_archivo = f'{nombre_zona[i]}_{nombre_division[i]}.csv' 
    else:
        nombre_archivo = f'{nombre_zona[i]}.csv' 
        
    ruta_completa = os.path.join(ruta_csv, nombre_archivo)

    eje_vertical_1 = "emission_time"
    eje_vertical_2 = "valid_time"

    nombres_eje_horizontal = ["dwi", "dwi_sin", "dwi_cos", "wind_max", "wind_med", "none", "none", "none", "shww_max", "shww_med", "mdts", "mdts_sin", "mdts_cos", "shts_max", "shts_med",
                              "none", "none", "none", "none", "none", "none", "none", "none", "none", "none"]

    # Filtrar nombres de columnas para eliminar los 'none'
    indices_validos = [index for index, nombre in enumerate(nombres_eje_horizontal) if 'none' not in nombre.lower()]
    nombres_columnas_filtradas = [nombres_eje_horizontal[index] for index in indices_validos]

    # Abrir el archivo para añadir contenido sin eliminar el existente
    with open(ruta_completa, 'a', newline='') as file:
        writer = csv.writer(file)

        # Escribir el encabezado si el archivo está vacío (posición actual del cursor es 0)
        if file.tell() == 0:
            writer.writerow([eje_vertical_1] + [eje_vertical_2] + nombres_columnas_filtradas)

        fecha = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

        if periodo == 1:
            emission_time = fecha.replace(hour=12, minute=0, second=0)
        elif periodo == 2:
            emission_time = fecha.replace(hour=18, minute=0, second=0)

        # Construir y escribir la fila con los datos
        for j in range(0, 9):
            incremento = timedelta(hours=3 * j)
            valid_time = fecha + incremento
            fila = [emission_time] + [valid_time] + [str(dat_final[j].get(k, '')) for k in indices_validos]
            writer.writerow(fila)

def funcion_principal(nombre_archivo, cod_boletin, ruta_csv): #
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()
    # print(contenido)
    boletin_recortado = {}
    secciones = {}
    dic_boletin = {}
    boletin_sep_fen = {}
    boletin_sep_zona = {}
    boletin_sep_temp = {}
    dat_boletin = {}
    dat_final = {}
    seccion_dic = []

    match = re.search(r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})_', nombre_archivo)
    
    if match:
        año, mes, día, hora, minutos = match.groups()
        hora = int(hora)
        if hora == 12:
            periodo = 1
        elif hora == 20:
            hora = 18
            periodo = 2
        else:
            print("No se pudo encontrar la fecha y la hora en el nombre del archivo.")

        fecha = f"{año}-{mes}-{día} {hora}:{minutos}:00"

    else:
        print("No se pudo encontrar la fecha y la hora en el nombre del archivo.")

    contenido = re.sub(r'^.*?(PREDICCION VALIDA PARA LAS PROXIMAS 24 HORAS\.|PREDICCION VALIDA PARA LAS PROXIMAS 24 HORAS:)', '', contenido, flags=re.DOTALL)
    contenido = re.sub(r'TENDENCIA DE LOS AVISOS PARA LAS SIGUIENTES 24 HORAS\..*', '', contenido, flags=re.DOTALL)

    matches = re.finditer(r'(AGUAS COSTERAS DE .*?)(?=AGUAS COSTERAS DE|\Z)', contenido, re.DOTALL)


    for i, match in enumerate(matches): 
        secciones[i] = match.group(1)

    # boletin_recortado = fecha + '\n\n' # Preparar el texto de salida

    num_zonas, num_divisiones, div_por_zona, dic_divisiones, zona_de_la_division, nombre_division, nombre_zona = parametros_zonas_y_divisiones(cod_boletin)

    for i, seccion in secciones.items():
        (boletin_recortado[i], seccion) = generar_lineas(seccion, fecha, div_por_zona, dic_divisiones, i)
        seccion_dic.append(seccion)
    
    dic_boletin, procesar_fenomeno_por_zonas = ordenar_lineas(seccion_dic, fecha, cod_boletin, div_por_zona, dic_divisiones, num_zonas, num_divisiones) 
    # print(procesar_fenomeno_por_zonas)
    for i in range(num_divisiones):    
        
        boletin_sep_fen[i] = separar_lineas_temporalmente(dic_boletin[i], fecha)

    boletin_sep_zona = ordenar_fenomenos_por_zonas(boletin_sep_fen, procesar_fenomeno_por_zonas, cod_boletin, div_por_zona, dic_divisiones, num_zonas, num_divisiones)
    
    for i in range(num_divisiones): 

        boletin_sep_temp[i] = ordenar_fenomenos_temporalmente(boletin_sep_zona[i], periodo)
        
        dat_boletin[i] = traducir(boletin_sep_temp[i])

    dat_final = reducir_unico_valor_por_campo(dat_boletin, div_por_zona, num_zonas, num_divisiones)

    for i in range(num_divisiones): 

        convertir_csv(dat_final[i], ruta_csv, fecha, periodo, nombre_zona, nombre_division, i)

    return boletin_recortado, dic_boletin, boletin_sep_fen, boletin_sep_zona, boletin_sep_temp, dat_boletin, dat_final
