import re
import csv
import os
import shutil
import pandas as pd
from datetime import datetime, timedelta
import math 
from math import sqrt, atan2, degrees

def vaciar_directorio(directorio):
    
    shutil.rmtree(directorio, ignore_errors=True)
    
    os.makedirs(directorio, exist_ok=True)

def ordenar_claves_segun_linea(pattern, text):
    # print(pattern, text)
    match = re.search(pattern, text, re.IGNORECASE)
    return match.start() if match else float('inf')

def parametros_zonas_y_divisiones(cod_boletin): #se encarga de coger el boletin ya filtrado por zonas y foltrarlo por fenomenos en viento, mar de viendo, mar de fondo, meteoros y visibilidad
    
    # print(cod_boletin)
    num_zonas = claves_zonas_y_divisiones(None, cod_boletin, 1)
    num_divisiones = claves_zonas_y_divisiones(None, cod_boletin, 2)


    div_por_zona = {i: [] for i in range(num_zonas)}  
    nombre_division = {i: [] for i in range(num_divisiones)}  
    nombre_zona = {i: [] for i in range(num_divisiones)}  
    zona_de_la_division = {i: [] for i in range(num_divisiones)}  
    
    k = 0

    for i in range(num_zonas):
        num_div = (claves_zonas_y_divisiones(i, cod_boletin, 2))
        div_por_zona[i] = len(num_div)
        if len(num_div) == 1:
            nombre_division[k] = num_div[0]
            zona_de_la_division[k] = i
            nombre_zona[k] = claves_zonas_y_divisiones(zona_de_la_division[k], cod_boletin, 1)
            k+=1
        else:
            for l in range(0, len(num_div)):
                nombre_division[k] = num_div[l]
                zona_de_la_division[k] = i
                nombre_zona[k] = claves_zonas_y_divisiones(zona_de_la_division[k], cod_boletin, 1)
                k+=1


    return num_zonas, num_divisiones, div_por_zona, zona_de_la_division, nombre_division, nombre_zona

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

def claves_generar_lineas(lugar): #Separar las lineas del boletin cuando falten los puntos finales
    
    claves = []

    if lugar == "no_zona":
        claves = [
            r"(-|;)\s?AMBAS\s*ZONAS",
            r"(-|;)\s?TODAS\s?LAS\s?ZONAS",
            r"(-|;)\s?RESTO",
            r"(-|;)\s?EN EL RESTO",
        ]

    elif lugar == "norte":
        claves = [
            r"(-|;)\s?AL\s?NORTE\s*",
            r"(-|;)\s?\s?NORTE\s*DE",
            r"(-|;)\s?ENTRE",
            r"(-|;)\s?ESTE\s?DE\s?SISAGRAS"
            r"- ESTE DE CABO SAN ADRIAN:"
        ]

    elif lugar == "sur":
        claves = [
            r"(-|;)\s?AL\s?SUR\s*",
            r"(-|;)\s?SUR\s*DE",
            r"(-|;)\s?ENTRE",
            r"(-|;)\s?OESTE\s?DE\s?SISAGRAS"
            r"- OESTE DE CABO SAN ADRIAN"
        ]

    elif lugar == "este":
        claves = [
            r"(-|;)\s?(AL)?\s*ESTE\s*DE",
        ]

    elif lugar == "oeste":
        claves = [
            r"(-|;)\s?(AL)?\s?OESTE\s*DE", 
        ]

    elif lugar == "ciudad":
        claves = [
            "- DE GUADALQUIVIR",      
        ]

    elif lugar == "trafalgar":
        claves = [
            "- DE CABO ROCHE",
        ]

    elif lugar == "tarifa":
        claves = [
            "- DE PUNTA CAMARINAL",
        ]

    elif lugar == "algeciras":
        claves = [
            "- DE PUNTA CARNERO",
        ]
        
    return claves

def claves_ordenar_lineas_por_zonas(lugar): #En el caso en que el boletin SI separe por zonas, busca las claves que lo determinan
    
    if lugar == "no_zona":
        claves_principio = [
            r"-?\s?(EN)?\s?AMBAS\s*ZONAS",
            r"-?\s?(EN)?\s?TODAS?\s?LAS?\s?ZONAS?",
            r"-?\s?(EN)?\s?TODO\s?EL\s?LITORAL",  
                
        ]
        
    elif lugar == "resto":
        claves_principio = [
            r"-?\s?RESTO",
            r"-?\s?EN\s?EL\s?RESTO",        
        ]      

    elif lugar == "norte":
        claves_principio = [
            r"-?\s?AL\s?NORTE\s*",
            r"-?\s?NORTE\s*DE",
            r"-?\s?EN\s?EL\s?NORTE",

            r"-\s?CERCA DE LA COSTA\s?AL\s?NORTE\s*DE",
            r"-?\s?ESTE\s?DE\s?SISARGAS",
            r"-?\s?ESTE\s?DE\s?CABO SAN ADRIAN:",
            r"-?\s?EN\s?TORNO\s?A\s?ORTEGAL",
            r"-?\s?(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*FISTERRA",
            r"-?\s?(ENTRE|DE)?\s*FISTERRA\s*(Y|-|A)\s*BARES",
            r"-?\s?(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*VILAN",
            r"-?\s?(ENTRE|DE)?\s*VILAN\s*(Y|-|A)\s*BARES",
            r"-?\s?(ENTRE|DE)?\s*VILAN\s*(Y|-|A)\s*SISARGAS",
            r"-?\s?(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*VILAN",
            r"-?\s?(ENTRE|DE)?\s*ORTEGAL\s*(Y|-|A)\s*BARES",
            r"-?\s?(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*ORTEGAL",
            r"-?\s?(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*ORTEGAL",
            r"-?\s?(ENTRE|DE)?\s*ORTEGAL\s*(Y|-|A)\s*SISARGAS",
            r"-?\s?(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*SISARGAS",
            r"-?\s?(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*BARES",          
            r"-?\s?(ENTRE|DE)?\s*PRIOR\s*(Y|-|A)\s*FISTERRA",
            r"-?\s?(ENTRE|DE)?\s*FISTERRA\s*(Y|-|A)\s*PRIOR",          
            r"-?\s?(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*PRIOR",
            r"-?\s?(ENTRE|DE)?\s*PRIOR\s*(Y|-|A)\s*BARES",
            r"-?\s?(ENTRE|DE)?\s*FISTERRA\s*(Y|-|A)\s*SISARGAS",
            r"-?\s?(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*FISTERRA",
            
            "AL NORTE DE LA ZONA: "
        ]
        

    elif lugar == "sur":
        claves_principio = [
            r"-?\s?AL\s?SUR\s*",
            r"-?\s?\s?SUR\s*DE",
            r"-?\s?EN\s?EL\s?SUR",

            r"-\s?CERCA DE LA COSTA\s?AL\s?SUR\s*DE",           
            r"-?\s?OESTE\s?(Y\s?SUR)?\s?DE\s?SISARGAS:",
            r"-?\s?OESTE\s?DE\s?CABO SAN ADRIAN:",         
            r"-?\s?(ENTRE|DE)?\s*FISTERRA\s*(Y|-|A)\s*CORRUBEDO",
            r"-?\s?(ENTRE|DE)?\s*CORRUBEDO\s*(Y|-|A)\s*FISTERRA",
            r"-?\s?(ENTRE|DE)?\s*VILAN\s*(Y|-|A)\s*CORRUBEDO",
            r"-?\s?(ENTRE|DE)?\s*CORRUBEDO\s*(Y|-|A)\s*VILAN",
            r"-?\s?(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*CORRUBEDO",
            r"-?\s?(ENTRE|DE)?\s*CORRUBEDO\s*(Y|-|A)\s*SISARGAS",

            "AL SUR DE LA ZONA: ",
        ]
        
    elif lugar == "oeste":
        claves_principio = [
            r"-?\s?AL\s?OESTE\s*", 
            r"-?\s?\s?OESTE\s*DE", 
            r"-?\s?EN\s?EL\s?OESTE",

            r"-?\s?EN EL EXTREMO (OCCIDENTAL|OESTE)",
            r"EL OESTE DE PENAS",
            r"-LITORAL OCCIDENTAL",

            "AL OESTE DE LA ZONA: ",
        ]
        
    elif lugar == "este":
        claves_principio = [
            r"-?\s?AL\s?ESTE\s*", 
            r"-?\s?\s?ESTE\s*DE", 
            r"-?\s?EN\s?EL\s?ESTE",

            r"-?\s?EN EL EXTREMO (ORIENTAL|ESTE)",
            r"EL ESTE DE PENAS",
            r"-LITORAL ORIENTAL",

            "AL ESTE DE LA ZONA: ",
        ]
        
    elif lugar == "ciudad":
        claves_principio = [
            "- DE GUADALQUIVIR",      
        ] 
        
    elif lugar == "trafalgar":
        claves_principio = [
            "- DE CABO ROCHE",
        ]
       
    elif lugar == "tarifa":
        claves_principio = [
            "- DE PUNTA CAMARINAL",
        ]
        
    elif lugar == "algeciras":
        claves_principio = [
            "- DE PUNTA CARNERO",
        ]
         
    return claves_principio

def claves_ordenar_lineas_por_tipo_fenomeno(fenomeno):

    if fenomeno == 1:
        claves_neg_principio = [
            r"RIZADA",
            r"MAREJADILLA",
            r"FUERTE\s*MAREJADA",
            r"MAREJADA",
            r"MUY\s*GRUESA",
            r"GRUESA",
            r"ARBOLADA",
            r"MONTANOSA",
            r"ENORME",
            r"(MAR)?E?\s*DEL?\s*FONDO",

            # r"-?\s?AMBAS\s*ZONAS",
            # r"-?\s?TODAS\s?LAS\s?ZONAS",
            # r"-?\s?TODO\s?EL\s?LITORAL", 
           
        ]
        claves_neg = [
            "AGUACEROS?",
            "TORMENTAS?",
            "LLUVIA",
            "LLOVIZNA",
            "VISIBILIDAD",
            "REGULAR",
            "MALA",
            "BRUMA",
            "CALIMA",
            "NIEBLA",
            "METROS",
            " M "
        ]

        claves = [
            r"(NORTE|SUR|ESTE|OESTE|SUROESTE|NOROESTE|SURESTE|NORESTE|N|S|E|W|NE|NW|SE|SW|VARIABLE|VRB)",        
            r"\d\s?((a|o)\s?\d)"
            r"FUERZA"
            
        ]

    elif fenomeno == 2:
        claves_neg_principio = []
        claves_neg = []
        claves = [
            r"RIZADA",
            r"MAREJADILLA",
            r"FUERTE\s*MAREJADA",
            r"MAREJADA",
            r"MUY\s*GRUESA",
            r"GRUESA",
            r"ARBOLADA",
            r"MONTANOSA",
            r"ENORME"
        ]

    elif fenomeno == 3:
        claves_neg_principio = []
        claves_neg = [
            r"FUERZA",
            r"(VARIABLE|VRB)",
            # r"COMBINADA",
            # r"SIGNIFICATIVA"

        ]
        claves = [
            r"MARE?\s*DE",
            r"DE\s*FONDO",
            r"MAR\s*FONDO",
            
        ]

    elif fenomeno == 4: #no necesaria la r
        claves_neg_principio = []
        claves_neg = []
        claves = [
            "AGUACEROS?",
            "TORMENTAS?",
            "L?LUVIA",
            "LLOVIZNA",
            "RACHAS",
            "PRECIPITACION",
        ]

    elif fenomeno == 5: #no necesaria la r
        claves_neg_principio = []
        claves_neg = []
        claves = [
            "VISIBILIDAD",
            "BUENA",
            "RE?GULAR",
            "MALA",
            "BRUMA",
            "CALIMA",
            "NIEBLA"
        ]
    
    return claves_neg_principio, claves_neg, claves

def claves_separar_lineas_temporalmente(fenomeno):

    claves = []

    if fenomeno == 1:
        claves_neg = [## Una palabra antes y otra despues
            "NO_ENCONTRADO",
            "BARES Y FISTERRA",
            "FISTERRA Y CORRUBEDO",  
            "FISTERRA Y SISARGAS",   
            "SISARGAS Y BARES",  
            "1 A 2",
            "2 A 3",
            "3 A 4",
            "4 A 5",
            "5 A 6",
            "6 A 7",
            "7 A 8",
            "8 A 9",
            "1 A 3",
            "1 A 4",
            "2 A 4",
            "2 A 5",
            "3 A 5",
            "3 A 6",
            "4 A 6",
            "4 A 7",
            "5 A 7",
            "5 A 8",
            "6 A 8",
            "6 A 9",
            "7 A 9",
    
        ]
        claves = [
            "NO_ENCONTRADO",
            r"(?:Y|,)?\s*TENDIENDO",
            r"(?:Y|,)?\s*AMAINANDO",
            r"(?:Y|,)?\s*ARRECIANDO",
            r"(?:Y|,)?\s*DISMINUYENDO",
            r"(?:Y|,)?\s*AUMENTANDO",
            r"(?:Y|,)?\s*TEMPORALMENTE",
            r"(?:Y|,)?\s*LOCALMENTE",
            r"(?:Y|,)?\s*OCASIONALMENTE",
            r"(?:Y|,)?\s*ROLANDO",
            r"(?:Y|,)?\s*QUEDANDO",
            r"(?:Y|,)?\s*SALVO",
            r"(?:Y|,|CON)?\s*AREAS",
            r"(?:Y|,| )\s*CON ",
            r",\s*\d+",
            ", A ",
            " Y A ",
            " Y ",
            ";",

        ]

    elif fenomeno == 2:
        claves_neg = [
            "NO_ENCONTRADO",

        ]
        claves = [
            "NO_ENCONTRADO",
            r"(?:Y|,)?\s*TENDIENDO",
            r"(?:Y|,)?\s*AMAINANDO",
            r"(?:Y|,)?\s*ARRECIANDO",
            r"(?:Y|,)?\s*DISMINUYENDO",
            r"(?:Y|,)?\s*AUMENTANDO",
            r"(?:Y|,)?\s*TEMPORALMENTE",
            r"(?:Y|,)?\s*LOCALMENTE",
            r"(?:Y|,)?\s*OCASIONALMENTE",
            r"(?:Y|,)?\s*ROLANDO",
            r"(?:Y|,)?\s*QUEDANDO",
            r"(?:Y|,)?\s*SALVO",
            r"(?:Y|,|CON)?\s*AREAS",
            r"(?:Y|,| )\s*CON ",
            ", A ",
            " Y A ",
            " Y ",

        ]

    elif fenomeno == 3:
        claves_neg = [
            "NO_ENCONTRADO",

        ]
        claves = [
            "NO_ENCONTRADO",
            r"(?:Y|,)?\s*TENDIENDO",
            r"(?:Y|,)?\s*AMAINANDO",
            r"(?:Y|,)?\s*ARRECIANDO",
            r"(?:Y|,)?\s*DISMINUYENDO",
            r"(?:Y|,)?\s*AUMENTANDO",
            r"(?:Y|,)?\s*TEMPORALMENTE",
            r"(?:Y|,)?\s*LOCALMENTE",
            r"(?:Y|,)?\s*OCASIONALMENTE",
            r"(?:Y|,)?\s*ROLANDO",
            r"(?:Y|,)?\s*QUEDANDO",
            r"(?:Y|,)?\s*SALVO",
            r"(?:Y|,|CON)?\s*AREAS",
            r"(?:Y|,| )\s*CON ",
            r",\s*\d+",
            ", A ",
            " Y A ",
            " Y ",
            
        ]

    elif fenomeno == 4:
        claves_neg = []
        claves = []

    elif fenomeno == 5:
        claves_neg = []
        claves = []

    return claves_neg, claves

def claves_ordenar_fenomenos_por_zonas(lugar):#En el caso en que el boletin NO separe por zonas, separa fenomenos locales
    
    claves = []
    
    if lugar == "no_zona":
        claves = [
            r"-?\s?AMBAS\s*ZONAS",
            r"-?\s?TODAS\s?LAS\s?ZONAS",
            r"-?\s?TODO\s?EL\s?LITORAL",
            
        ]

    elif lugar == "resto":
        claves = [
            r"-?\s?RESTO",
            r"-?\s?EN\s?EL\s?RESTO",
            
        ]

    elif lugar == "norte":
        claves = [
            r"AL\s?NORTE\s*(DE)?",
            r"EN\s?EL\s?NORTE",

            r"(EN|HACIA|CERCA\s?DE)\s?(TORNO\s?A|EL\s?AREA\s?DE)?\s?(BARES|ORTEGAL)",
            
            r"-?\s?ESTE\s?DE\s?SISARGAS",
            r"-?\s?ESTE\s?DE\s?CABO SAN ADRIAN:",
            r"(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*FISTERRA",
            r"(ENTRE|DE)?\s*FISTERRA\s*(Y|-|A)\s*BARES",
            r"(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*VILAN",
            r"(ENTRE|DE)?\s*VILAN\s*(Y|-|A)\s*BARES",
            r"(ENTRE|DE)?\s*VILAN\s*(Y|-|A)\s*SISARGAS",
            r"(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*VILAN",
            r"(ENTRE|DE)?\s*ORTEGAL\s*(Y|-|A)\s*BARES",
            r"(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*ORTEGAL",
            r"(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*ORTEGAL",
            r"(ENTRE|DE)?\s*ORTEGAL\s*(Y|-|A)\s*SISARGAS",
            r"(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*SISARGAS",
            r"(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*BARES",          
            r"(ENTRE|DE)?\s*PRIOR\s*(Y|-|A)\s*FISTERRA",
            r"(ENTRE|DE)?\s*FISTERRA\s*(Y|-|A)\s*PRIOR",          
            r"(ENTRE|DE)?\s*BARES\s*(Y|-|A)\s*PRIOR",
            r"(ENTRE|DE)?\s*PRIOR\s*(Y|-|A)\s*BARES",
            r"(ENTRE|DE)?\s*FISTERRA\s*(Y|-|A)\s*SISARGAS",
            r"(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*FISTERRA",
            
        ]

    elif lugar == "sur":
        claves = [
            r"AL\s?SUR\s*(DE)?",
            r"EN\s?EL\s?SUR",

            r"(EN|HACIA|CERCA\s?DE)\s?(TORNO\s?A|EL\s?AREA\s?DE)?\s?(FISTERRA)",
         
            r"OESTE\s?(Y\s?SUR)?\s?DE\s?SISARGAS:",
            r"OESTE\s?DE\s?CABO SAN ADRIAN:",         
            r"(ENTRE|DE)?\s*FISTERRA\s*(Y|-|A)\s*CORRUBEDO",
            r"(ENTRE|DE)?\s*CORRUBEDO\s*(Y|-|A)\s*FISTERRA",
            r"(ENTRE|DE)?\s*VILAN\s*(Y|-|A)\s*CORRUBEDO",
            r"(ENTRE|DE)?\s*CORRUBEDO\s*(Y|-|A)\s*VILAN",
            r"(ENTRE|DE)?\s*SISARGAS\s*(Y|-|A)\s*CORRUBEDO",
            r"(ENTRE|DE)?\s*CORRUBEDO\s*(Y|-|A)\s*SISARGAS",

        ]
    elif lugar == "oeste":
        claves = [
            r"-?\s?(AL)?\s?OESTE\s*DE", 
            r"-?\s?EN\s?EL\s?OESTE",

            r"-?\s?EN EL EXTREMO (OCCIDENTAL|OESTE)",
            r"EL OESTE DE PENAS",
            r"-LITORAL OCCIDENTAL",

            ]
    elif lugar == "este":
        claves = [
            r"-?\s?(AL)?\s*ESTE\s*DE",
            r"-?\s?EN\s?EL\s?ESTE",

            r"-?\s?EN EL EXTREMO (ORIENTAL|ESTE)",
            r"EL ESTE DE PENAS",
            r"-LITORAL ORIENTAL",
        ]
    elif lugar == "ciudad":
        claves = [
            "- DE GUADALQUIVIR",      
        ] 
       
    elif lugar == "trafalgar":
        claves = [
            "- DE CABO ROCHE",
        ]
        
    elif lugar == "tarifa":
        claves = [
            "- DE PUNTA CAMARINAL",
        ]
        
    elif lugar == "algeciras":
        claves = [
            "- DE PUNTA CARNERO",
        ]
    
    return claves

def claves_ordenar_fenomenos_temporalmente(valor, periodo, funcion):

    if periodo == 1:
        dic = {
            "TARDE": 2,
            "NOCHE": 3,
            "MEDIANOCHE": 4,
            "MADRUGADA": 5,
            r"FINAL\s*DE\s*LA\s*MADRUGADA": 6,
            r"AVANZADA\s*LA\s*MADRUGADA": 6,
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
            "MANANA": 5,
            "MEDIODIA": 6,
            "TARDE": 7,
            r"DIA \d+": 3,
            "DIA": 6,
    }
    if funcion == 1: #Traduccion
        return dic.get(valor, 'Desconocido')
    elif funcion == 2:
        return dic #Enumeracion

def claves_traducir(valor, fenomeno, variable, funcion):
    if fenomeno == 1:
        if variable == 1:
            clave_neg = {
                "NO_ENCONTRADO",
                "EN EL NORTE",
                "NORTE DE",
                "EN EL SUR",
                "SUR DE",
                "EN EL OESTE",
                "OESTE DE",
                "EN EL ESTE",
                "ESTE DE",
            }
            clave = {
                r"(NORTE|N)\s*(O|Y|A|-)\s*(NOROESTE|NW)": 337.5,
                r"(NOROESTE|NW)\s*(O|Y|A|-)\s*(NORTE|N)": 337.5,
                r"(NOROESTE|NW)\s*(O|Y|A|-)\s*(OESTE|W)": 292.5,
                r"(OESTE|W)\s*(O|Y|A|-)\s*(NOROESTE|NW)": 292.5,
                r"(OESTE|W)\s*(O|Y|A|-)\s*(SUR?D?OESTE|SW)": 247.5,
                r"(SUR?D?OESTE|SW)\s*(O|Y|A|-)\s*(OESTE|W)": 247.5,
                r"(SUR?D?OESTE|SW)\s*(O|Y|A|-)\s*(SUR|S)": 202.5,
                r"(SUR|S)\s*(O|Y|A|-)\s*(SUR?D?OESTE|SW)": 202.5,
                r"(SUR|S)\s*(O|Y|A|-)\s*(SUR?D?ESTE|SE)": 157.5,
                r"(SUR?D?ESTE|SE)\s*(O|Y|A|-)\s*(SUR|S)": 157.5,
                r"(SUR?D?ESTE|SE)\s*(O|Y|A|-)\s*(ESTE|E)": 112.5,
                r"(ESTE|E)\s*(O|Y|A|-)\s*(SUR?D?ESTE|SE)": 112.5,
                r"(ESTE|E)\s*(O|Y|A|-)\s*(NORD?ESTE|NE)": 67.5,
                r"(NORD?ESTE|NE)\s*(O|Y|A|-)\s*(ESTE|E)": 67.5,
                r"(NORD?ESTE|NE)\s*(O|Y|A|-)\s*(NORTE|N)": 22.5,
                r"(NORTE|N)\s*(O|Y|A|-)\s*(NORD?ESTE|NE)": 22.5,
                r"(NOROESTE|NW)": 315,
                r"(NORD?ESTE|NE)": 45,
                r"(SUR?D?OESTE|SW)": 225,
                r"(SUR?D?ESTE|SE)": 135,
                r"(NORTE|N|COMPONENTE\s*N)": 0,
                r"(SUR|S|COMPONENTE\s*S)": 180,
                r"(OESTE|W|COMPONENTE\s*W)": 270,
                r"(ESTE|E|COMPONENTE\s*E)": 90,
                "VARIABLE": "X"
            }
        elif variable == 2:
            clave_neg = {
                "NO_ENCONTRADO",
            }
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
        elif variable == 3:
            clave_neg = {
                "NO_ENCONTRADO",
            }
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
    
    elif fenomeno == 2:
        if variable == 1:
            clave_neg = {
                
            }
            clave = {}
        elif variable == 2:
            clave_neg = {
                "NO_ENCONTRADO",
            }
            clave = {
                r"RIZADA\s*O\s*MAREJADILLA": 0.5,
                r"MAREJADILLA\s*O\s*RIZADA": 0.5,
                r"MAREJADILLA\s*O\s*MAREJADA": 1.25,
                r"MAREJADA\s*O\s*MAREJADILLA": 1.25,
                r"MAREJADA\s*O\s*FUERTE\s*MAREJADA": 2.5,
                r"FUERTE\s*MAREJADA\s*O\s*MAREJADA": 2.5,
                r"FUERTE\s*MAREJADA\s*O\s*GRUESA": 4,
                r"GRUESA\s*O\s*FUERTE\s*MAREJADA": 4,
                r"GRUESA\s*O\s*MUY\s*GRUESA": 6,
                r"MUY\s*GRUESA\s*O\s*GRUESA": 6,
                r"MUY\s*GRUESA\s*O\s*ARBOLADA": 9,
                r"ARBOLADA\s*O\s*MUY\s*GRUESA": 9,
                r"ARBOLADA\s*O\s*MONTANOSA": 14,
                r"MONTANOSA\s*O\s*ARBOLADA": 14,
                r"MONTANOSA\s*O\s*ENORME": 16,
                r"ENORME\s*O\s*MONTANOSA": 16,
                r"RIZADA": 0.1,
                r"MAREJADILLA": 0.5,
                r"FUERTE\s*MAREJADA": 2.5,
                r"MAREJADA": 1.25,
                r"MUY\s*GRUESA": 6,
                r"GRUESA": 4,
                r"ARBOLADA": 9,
                r"MONTANOSA": 14,
                r"ENORME": 16,
                # "NO_CLAVE": 1.5
            }
        elif variable == 3:
            clave_neg = {
                "NO_ENCONTRADO",
            }
            clave = {
                r"RIZADA\s*O\s*MAREJADILLA": 0.25,
                r"MAREJADILLA\s*O\s*RIZADA": 0.25,
                r"MAREJADILLA\s*O\s*MAREJADA": 0.75,
                r"MAREJADA\s*O\s*MAREJADILLA": 0.75,
                r"MAREJADA\s*O\s*FUERTE\s*MAREJADA": 1.75,
                r"FUERTE\s*MAREJADA\s*O\s*MAREJADA": 1.75,
                r"FUERTE\s*MAREJADA\s*O\s*GRUESA": 3.125,
                r"GRUESA\s*O\s*FUERTE\s*MAREJADA": 3.125,
                r"GRUESA\s*O\s*MUY\s*GRUESA": 5,
                r"MUY\s*GRUESA\s*O\s*GRUESA": 5,
                r"MUY\s*GRUESA\s*O\s*ARBOLADA": 7.5,
                r"ARBOLADA\s*O\s*MUY\s*GRUESA": 7.5,
                r"ARBOLADA\s*O\s*MONTANOSA": 11.5,
                r"MONTANOSA\s*O\s*ARBOLADA": 11.5,
                r"MONTANOSA\s*O\s*ENORME": 15,
                r"ENORME\s*O\s*MONTANOSA": 15,
                r"RIZADA": 0.1,
                r"MAREJADILLA": 0.25,
                r"FUERTE\s*MAREJADA": 1.75,
                r"MAREJADA": 0.75,
                r"MUY\s*GRUESA": 5,
                r"GRUESA": 3.125,
                r"ARBOLADA": 7.5,
                r"MONTANOSA": 11.5,
                r"ENORME": 15,
                # "NO_CLAVE": 1
            }

    elif fenomeno == 3:
        if variable == 1:
            clave_neg = {
                "NO_ENCONTRADO",
            }
            clave = {
                r"(NORTE|N)\s*(O|Y|A|-)\s*(NOROESTE|NW)": 337.5,
                r"(NOROESTE|NW)\s*(O|Y|A|-)\s*(NORTE|N)": 337.5,
                r"(NOROESTE|NW)\s*(O|Y|A|-)\s*(OESTE|W)": 292.5,
                r"(OESTE|W)\s*(O|Y|A|-)\s*(NOROESTE|NW)": 292.5,
                r"(OESTE|W)\s*(O|Y|A|-)\s*(SUR?D?OESTE|SW)": 247.5,
                r"(SUR?D?OESTE|SW)\s*(O|Y|A|-)\s*(OESTE|W)": 247.5,
                r"(SUR?D?OESTE|SW)\s*(O|Y|A|-)\s*(SUR|S)": 202.5,
                r"(SUR|S)\s*(O|Y|A|-)\s*(SUR?D?OESTE|SW)": 202.5,
                r"(SUR|S)\s*(O|Y|A|-)\s*(SUR?D?ESTE|SE)": 157.5,
                r"(SUR?D?ESTE|SE)\s*(O|Y|A|-)\s*(SUR|S)": 157.5,
                r"(SUR?D?ESTE|SE)\s*(O|Y|A|-)\s*(ESTE|E)": 112.5,
                r"(ESTE|E)\s*(O|Y|A|-)\s*(SUR?D?ESTE|SE)": 112.5,
                r"(ESTE|E)\s*(O|Y|A|-)\s*(NORD?ESTE|NE)": 67.5,
                r"(NORD?ESTE|NE)\s*(O|Y|A|-)\s*(ESTE|E)": 67.5,
                r"(NORD?ESTE|NE)\s*(O|Y|A|-)\s*(NORTE|N)": 22.5,
                r"(NORTE|N)\s*(O|Y|A|-)\s*(NORD?ESTE|NE)": 22.5,
                r"(NOROESTE|NW)": 315,
                r"(NORD?ESTE|NE)": 45,
                r"(SUR?D?OESTE|SW)": 225,
                r"(SUR?D?ESTE|SE)": 135,
                r"(NORTE|N|COMPONENTE\s*N)": 0,
                r"(SUR|S|COMPONENTE\s*S)": 180,
                r"(OESTE|W|COMPONENTE\s*W)": 270,
                r"(ESTE|E|COMPONENTE\s*E)": 90,
                "VARIABLE": "X",
                # "NO_CLAVE":"X",
            }
        elif variable == 2:
            clave_neg = {
                "NO_ENCONTRADO",
            }
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
        elif variable == 3:
            clave_neg = {
                "NO_ENCONTRADO",
            }
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

    elif fenomeno == 4:
        if variable == 1:
            clave_neg = {}
            clave = {}
        elif variable == 2:
            clave_neg = {}
            clave = {}
        elif variable == 3:
            clave_neg = {}
            clave = {}
    elif fenomeno == 5:
        if variable == 1:
            clave_neg = {}
            clave = {}
        elif variable == 2:
            clave_neg = {}
            clave = {}
        elif variable == 3:
            clave_neg = {}
            clave = {}

    if funcion == 1: #Traduccion
        return clave.get(valor)
    elif funcion == 2:
        return clave_neg, clave #Enumeracion

def generar_lineas(seccion, cod_boletin, i):

    dic_divisiones = claves_zonas_y_divisiones(i, cod_boletin, 2)
    div_por_zona = len(dic_divisiones)
 
    
    boletin_recortado = ""
    seccion = re.sub(r'^(.*?):', '', seccion)# Eliminar aguas costeras y el nombre de la región en el encabezado de cada sección
    
    seccion = re.sub(r'(?<!\.)\n', '', seccion) # Eliminar saltos de línea donde no hay punto final
    
    if div_por_zona != 1:
        claves_saltos = ""
        for l in range(div_por_zona):
            claves_saltos += '|'.join(claves_generar_lineas(dic_divisiones[l])) + '|'

        claves_saltos += '|'.join(claves_generar_lineas("no_zona"))
        seccion = re.sub(fr'({claves_saltos})', r'\n\1', seccion, flags=re.IGNORECASE)
    
    
    seccion = re.sub(r'(\.)(?!\s*$)', r'\1\n', seccion) # Añadir salto de línea después de cada punto y eliminar espacio al principio de la línea siguiente
    
    seccion = re.sub(r'^\s+', '', seccion, flags=re.MULTILINE) # Eliminar espacios al principio de cada línea

    boletin_recortado = f"{seccion}"# Formatear la sección con el identificador de zona y contenido modificado
    
    return boletin_recortado, seccion

def escribir_lineas(procesar_zona_principio, per_zona, dic_boletin, div_por_zona, divisor, other, k, m):#subfuncion de ordenar lineas

    if procesar_zona_principio == False:
         for l in range(div_por_zona):
            if divisor: 
                dic_boletin[k + l][m].append(divisor + other)
            else:
                dic_boletin[k + l][m].append(other)
    else:
        if not any(per_zona):
            for l in range(div_por_zona):
                if divisor: 
                    dic_boletin[k + l][m].append(divisor + other)
                else:
                    dic_boletin[k + l][m].append(other)
        
        else:
            for l in range(div_por_zona):
                if per_zona[l]:
                    if divisor: 
                        dic_boletin[k + l][m].append(divisor + other)
                    else:
                        dic_boletin[k + l][m].append(other)

    return dic_boletin

def ordenar_lineas(seccion, fecha, cod_boletin, num_zonas, num_divisiones): #se encarga de coger el boletin ya filtrado por zonas y foltrarlo por fenomenos en viento, mar de viendo, mar de fondo, meteoros y visibilidad
    
    dic_boletin = {i: {j: [] for j in range(1, 6)} for i in range(num_divisiones)}
        

    claves_neg_principio = {i: [] for i in range(1, 6)} 
    claves_neg = {i: [] for i in range(1, 6)}
    claves = {i: [] for i in range(1, 6)}

    lineas = []
    
    for i in range(1,6):
        claves_neg_principio[i], claves_neg[i], claves[i] = claves_ordenar_lineas_por_tipo_fenomeno(i)
        claves_neg_principio[i] = '|'.join([r'^' + clave for clave in claves_neg_principio[i]])
        claves_neg[i] = '|'.join(claves_neg[i])
    
    claves_meteoros = {}
    claves_meteoros = claves[4] + claves[5]

    procesar_zona = [True] * num_zonas
    procesar_zona_principio = False
    
    k = 0
    
    for j in range(num_zonas):

        lineas = seccion[j].split('\n')
        
        dic_divisiones = claves_zonas_y_divisiones(j, cod_boletin, 2)
        div_por_zona = len(dic_divisiones)

        if div_por_zona == 1:
            procesar_zona[j]= False

        clave_sep_primer = False
        clave_resto = False
        p = 0   #Añade separacion de zona al principio si se olvido  

        if div_por_zona != 1:
            
            claves_principio_zona = [[] for _ in range(div_por_zona)]
            union_claves_principio_zona = ""

            for l in range(div_por_zona):
                claves_principio_zona[l] = claves_ordenar_lineas_por_zonas(dic_divisiones[l])
                claves_principio_zona[l] = [r'^' + clave for clave in claves_principio_zona[l]]
                union_claves_principio_zona += '|'.join(claves_principio_zona[l]) + '|'
            union_claves_principio_zona = union_claves_principio_zona.rstrip('|')

            claves_principio_no_zona = claves_ordenar_lineas_por_zonas("no_zona")
            claves_principio_no_zona = [r'^' + clave for clave in claves_principio_no_zona]
            union_claves_principio_no_zona = '|'.join(claves_principio_no_zona) 
           
            claves_principio_resto = claves_ordenar_lineas_por_zonas("resto")
            claves_principio_resto = [r'^' + clave for clave in claves_principio_resto]
            union_claves_principio_resto = '|'.join(claves_principio_resto)
            
            for linea in lineas:
                if re.search(union_claves_principio_zona, linea, re.IGNORECASE):
                    procesar_zona[j]= False
                    if linea == lineas[0]:
                        clave_sep_primer = True
                    p+=1   

                elif re.search(union_claves_principio_resto, linea, re.IGNORECASE) or re.search(union_claves_principio_no_zona, linea, re.IGNORECASE):
                    procesar_zona[j]= False
                    clave_resto = True
                    if linea == lineas[0]:
                        clave_sep_primer = True
            
            if (p == div_por_zona - 1 or clave_resto) and not clave_sep_primer:
                ultima_clave = claves_principio_zona[0][-1]
                lineas[0] = ultima_clave + lineas[0]

        if procesar_zona[j] == True or div_por_zona == 1: 
            procesar_zona_principio = False 
        else:
            procesar_zona_principio = True

        per_zona = [False] * div_por_zona
        resto_zona = [True] * div_por_zona
          
        for linea in lineas:
            primer_fen = False
            divisor = None

            if procesar_zona_principio == True:
                if re.search(union_claves_principio_zona, linea, re.IGNORECASE) or re.search(union_claves_principio_resto, linea, re.IGNORECASE):
                    per_zona = [False] * div_por_zona
                    
                    if re.search(union_claves_principio_resto, linea, re.IGNORECASE):
                        per_zona = resto_zona
                    else:
                        for l in range(div_por_zona):
                            for clave in claves_principio_zona[l]:
                                if re.search(clave, linea, re.IGNORECASE):
                                    per_zona[l] = True
                                    resto_zona[l] = False

                elif re.search(union_claves_principio_no_zona, linea, re.IGNORECASE):                            
                    per_zona = [False] * div_por_zona

            m = 0 #Quitar para completar patrones
            for i in range(1,4):

                claves[i] = sorted(claves[i], key=lambda orden: ordenar_claves_segun_linea(orden, linea))
                
                if claves_neg[i] and re.search(claves_neg[i], linea, re.IGNORECASE):
                    continue

                if claves_neg_principio[i] and re.search(claves_neg_principio[i], linea, re.IGNORECASE):
                    continue
                
                if re.search(claves[i][0], linea, re.IGNORECASE):
                    partes = re.split(f'({claves[i][0]})', linea, 1, flags=re.IGNORECASE)
                    if primer_fen:
                        linea = partes[2]
                        other = partes[0]

                        dic_boletin = escribir_lineas(procesar_zona_principio, per_zona, dic_boletin, div_por_zona, divisor, other, k, m)
                             
                        divisor = partes[1]
                    
                    primer_fen = True
                    m=i

            claves_meteoros = sorted(claves_meteoros, key=lambda orden: ordenar_claves_segun_linea(orden, linea))
            
            if claves_meteoros[0] in claves[5]:
                indices_met = [5, 4]
            else:
                indices_met = [4, 5] 

            for i in indices_met:
                claves[i] = sorted(claves[i], key=lambda orden: ordenar_claves_segun_linea(orden, linea))

                if claves_neg[i] and re.search(claves_neg[i], linea, re.IGNORECASE):
                    continue

                if claves_neg_principio[i] and re.search(claves_neg_principio[i], linea, re.IGNORECASE):
                    continue
                
                if re.search(claves[i][0], linea, re.IGNORECASE):
                    partes = re.split(f'({claves[i][0]})', linea, 1, flags=re.IGNORECASE)
                    if primer_fen:
                        linea = partes[2]
                        other = partes[0]
                        
                        dic_boletin = escribir_lineas(procesar_zona_principio, per_zona, dic_boletin, div_por_zona, divisor, other, k, m)
                             
                        divisor = partes[1]
                    
                    primer_fen = True
                    m=i
            if m != 0: #Quitar para completar patrones

                dic_boletin = escribir_lineas(procesar_zona_principio, per_zona, dic_boletin, div_por_zona, divisor, linea, k, m)
         
            # else:
            #     if linea != "":
            #         print(linea, fecha) 
        k += div_por_zona  
        
    return dic_boletin, procesar_zona

def separar_lineas_temporalmente(dic_boletin, fecha): #separa cada fenomeno en cachos temporales temporalmente,
    
    temp_boletin = {i: [] for i in range(1, 6)}

    for i in range(1,6):# hasta 6
        
        claves_neg, divisores_ord = claves_separar_lineas_temporalmente(i)
        encontrado_divisor=True
        
        for fenomeno in dic_boletin[i]:
            encontrado_divisor=True
            divisor = None
            j=0

            while encontrado_divisor and j < len(divisores_ord):

                divisores_ord = sorted(divisores_ord, key=lambda orden: ordenar_claves_segun_linea(orden, fenomeno))
                claves_neg = sorted(claves_neg, key=lambda orden: ordenar_claves_segun_linea(orden, fenomeno))
                # print(fenomeno, divisores_ord[j], claves_neg[j])

                encontrado_divisor = False
                
                if divisores_ord and re.search(divisores_ord[j], fenomeno, re.IGNORECASE):
                    
                    patron = rf'(\S+\s?)?({divisores_ord[j]})(\s?\S+)?'
                    match = re.search(patron, fenomeno, re.IGNORECASE)
                    
                    if match:
                        palabra_antes = match.group(1) if match.group(1) else ""
                        palabra_medio = match.group(2)
                        palabra_despues = match.group(3) if match.group(3) else ""
                        expresion = f"{palabra_antes}{palabra_medio}{palabra_despues}".strip()
                    
                    # print(fenomeno, expresion)

                    if claves_neg:
                        for neg in claves_neg:
                            if re.search(divisores_ord[j], neg, re.IGNORECASE) and re.search(neg, expresion, re.IGNORECASE):
                                encontrado_divisor = True
                                j+=1
                                break
                        
                    if not encontrado_divisor:
                        partes = re.split(f'({divisores_ord[j]})', fenomeno, 1, flags=re.IGNORECASE)
                        encontrado_divisor = True
                        fenomeno = partes[2]
                        other = partes[0]
                        if divisor: 
                            temp_boletin[i].append(divisor + other)
                        else:
                            temp_boletin[i].append(other)
                        divisor = partes[1]
                        j=0

            if divisor:    
                temp_boletin[i].append(divisor + fenomeno)
            else:
                temp_boletin[i].append(fenomeno)
            
    return temp_boletin

def ordenar_fenomenos_por_zonas(boletin_sep_fen, procesar_zona, cod_boletin, num_zonas, num_divisiones):#coloca cada fenomeno en el tiempo correcto

    dic_divisiones = []
    claves_filtro_zona = []
    per_zona = []
    boletin_sep_zona = {}
    per_zona_otro = []

    for j in range(num_divisiones):
        boletin_sep_zona[j] = {i: [] for i in range(1, 6)}

    k = 0

    for j in range(num_zonas):
        dic_divisiones = claves_zonas_y_divisiones(j, cod_boletin, 2)
        div_por_zona = len(dic_divisiones)
       
        if procesar_zona[j] == False:
            for i in range(1, 6):
                for l in range(div_por_zona):
                    boletin_sep_zona[k + l][i] = boletin_sep_fen[k + l][i]
            k += div_por_zona
        else:
            claves_zona = [[] for _ in range(div_por_zona)]
            union_claves_zona = ""
            
            for l in range(div_por_zona):
                claves_zona[l] = claves_ordenar_fenomenos_por_zonas(dic_divisiones[l])
                union_claves_zona += '|'.join(claves_zona[l]) + '|'
            union_claves_zona = union_claves_zona.rstrip('|')
            
            claves_no_zona = claves_ordenar_fenomenos_por_zonas("no_zona")
            union_claves_no_zona = '|'.join(claves_no_zona) 
           
            claves_resto = claves_ordenar_fenomenos_por_zonas("resto")
            union_claves_resto = '|'.join(claves_resto)
        
            for i in range(1, 6):
               
                resto_zona = [True] * div_por_zona
        
                for fenomeno in boletin_sep_fen[j][i]:

                    per_zona = [False] * div_por_zona
                    
                    if re.search(union_claves_resto, fenomeno, re.IGNORECASE):
                        per_zona = resto_zona
                    elif re.search(union_claves_no_zona, fenomeno, re.IGNORECASE):                            
                        per_zona = [False] * div_por_zona
                    else:
                        for l in range(div_por_zona):
                            for clave in claves_zona[l]:
                                if re.search(clave, fenomeno, re.IGNORECASE):
                                    per_zona[l] = True
                                    resto_zona[l] = False

                    if not any(per_zona):
                        for l in range(div_por_zona):
                            boletin_sep_zona[k + l][i].append(fenomeno)
                    else:
                        for l in range(div_por_zona):
                            if per_zona[l]:
                                boletin_sep_zona[k + l][i].append(fenomeno)

            k += div_por_zona

    return boletin_sep_zona

def ordenar_fenomenos_temporalmente(temp_boletin, periodo):#coloca cada fenomeno en el tiempo correcto

    claves_trad_temp = claves_ordenar_fenomenos_temporalmente(None, periodo, 2)

    claves_temp = '|'.join(claves_trad_temp)
    
    boletin_sep_temp = {}

    step = None
    step_anterior = None

    for j in range(0, 9):
        boletin_sep_temp[j] = {i: [] for i in range(1, 6)}

    for i in range(1,6):
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
                if re.search(r'(COMBINADA|SIGNIFICATIVA)', fenomeno, re.IGNORECASE) and i == 3:
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
                        if i == 2 and step_anterior is not None and step_anterior != step and (re.search('AUMENTANDO', fenomeno, re.IGNORECASE) or re.search('DISMINUYENDO', fenomeno, re.IGNORECASE)):
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
        dat_boletin[j] = {i: [] for i in range(1, 26)} 
    
    for i in range(1,6):

        clave_ang_0=False
        clave_max_0=False
        clave_med_0=False

        for j in range (0,9):
            
            claves_neg_trad_1, claves_trad_1 = claves_traducir(None, i, 1, 2)
            claves_neg_trad_2, claves_trad_2 = claves_traducir(None, i, 2, 2)
            claves_neg_trad_3, claves_trad_3 = claves_traducir(None, i, 3, 2)

            clave_ang=False
            clave_max=False
            clave_med=False
            

            total_fenomenos = len(dic_boletin[j][i])
            for idx, fenomeno in enumerate(dic_boletin[j][i]):
                
                for clave in claves_trad_1:  
                    pat_clave = r'\b' + clave + r'\b'  # Crear patrón de búsqueda para la clave actual
                    if re.search(pat_clave, fenomeno, re.IGNORECASE):  # Buscar si la clave está en el fenómeno
                        clave_negada = False  # Indicador para detectar si la clave está negada
                        
                        for neg in claves_neg_trad_1:
                            pat_neg = r'\b' + neg + r'\b' 
                            if re.search(pat_clave, neg, re.IGNORECASE) and re.search(pat_neg, fenomeno, re.IGNORECASE):
                                clave_negada = True  
                                break 
                        
                        if not clave_negada:
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

                            dat_boletin[j][i * 5 - 4].append(valor_numerico)
                            dat_boletin[j][i * 5 - 3].append(sin_dat)
                            dat_boletin[j][i * 5 - 2].append(cos_dat)

                            if j == 0:
                                clave_ang_0 = True
                            else:
                                clave_ang = True

                            break #Quitar hacer que pasen todos los fenomenos
                                        
                for clave in claves_trad_2:  
                    pat_clave = r'\b' + clave + r'\b'  
                    if re.search(clave, fenomeno, re.IGNORECASE):
                        dat_boletin[j][i * 5 - 1].append(claves_traducir(clave, i, 2, 1))
                        if j==0:
                            clave_max_0=True
                        else:
                            clave_max=True  
                        break   
                
                for clave in claves_trad_3:    
                    pat_clave = r'\b' + clave + r'\b'
                    if re.search(clave, fenomeno, re.IGNORECASE):
                        dat_boletin[j][i * 5].append(claves_traducir(clave, i, 3, 1))
                        if j==0:
                            clave_med_0=True
                        else:
                            clave_med=True  
                        break  

                if (idx == total_fenomenos - 1) and j!=0:
                    if not clave_ang:
                        dat_boletin[j][i * 5 - 4]=dat_boletin[j-1][i * 5 - 4]
                        dat_boletin[j][i * 5 - 3]=dat_boletin[j-1][i * 5 - 3]
                        dat_boletin[j][i * 5 - 2]=dat_boletin[j-1][i * 5 - 2]         

                    if not clave_max:
                        dat_boletin[j][i * 5 - 1]=dat_boletin[j-1][i * 5 - 1]

                    if not clave_med:
                        dat_boletin[j][i * 5]=dat_boletin[j-1][i * 5] 

                    if j==1:
                        if not clave_ang_0:
                            dat_boletin[0][i * 5 - 4]=dat_boletin[1][i * 5 - 4]
                            dat_boletin[0][i * 5 - 3]=dat_boletin[1][i * 5 - 3]
                            dat_boletin[0][i * 5 - 2]=dat_boletin[1][i * 5 - 2]         
                        
                        if not clave_max_0:
                            dat_boletin[0][i * 5 - 1]=dat_boletin[1][i * 5 - 1]

                        if not clave_med_0:
                            dat_boletin[0][i * 5]=dat_boletin[1][i * 5]  
                           

            if dat_boletin[j][i*5 - 4] == []:
                dat_boletin[j][i*5 - 4].append(claves_traducir("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 - 3] == []:
                dat_boletin[j][i*5 - 3].append(claves_traducir("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 - 2] == []:
                dat_boletin[j][i*5 - 2].append(claves_traducir("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 - 1] == []:
                dat_boletin[j][i*5 - 1].append(claves_traducir("NO_CLAVE", i, 2, 1))
            if dat_boletin[j][i*5] == []:
                dat_boletin[j][i*5].append(claves_traducir("NO_CLAVE", i, 3, 1))

    return dat_boletin

def reducir_unico_valor_por_campo(dat_boletin):#selecciona un unico valor dentro de cada intervalo temporal
    
    dat_final={}

    for j in range(0, 9):
        dat_final[j] = {i: [] for i in range(1, 26)}

    for j in range (0,9):
        for i in range(1,6):
        
            valores_numericos = []
            for valor in dat_boletin[j][5*i-3]:
                if valor is not None:
                    try:
                        numero = float(valor)
                        valores_numericos.append(numero)
                    except ValueError:
                        continue
            if valores_numericos:
                suma_valores=sum(valores_numericos)
                media = suma_valores / len(valores_numericos)
                dat_final[j][5*i-3] = media
            else:
                dat_final[j][5*i-3] = None

            valores_numericos = []
            for valor in dat_boletin[j][5*i-2]:
                if valor is not None:
                    try:
                        numero = float(valor)
                        valores_numericos.append(numero)
                    except ValueError:
                        continue
            if valores_numericos:
                suma_valores=sum(valores_numericos)
                media = suma_valores / len(valores_numericos)
                dat_final[j][5*i-2] = media
            else:
                dat_final[j][5*i-2] = None

            if dat_final[j][5*i-2] is not None and dat_final[j][5*i-3] is not None:
                cuad = sqrt(dat_final[j][5*i-2]**2 + dat_final[j][5*i-3]**2)
                if cuad != 0:
                    dat_final[j][5*i-3] = dat_final[j][5*i-3] / cuad
                    dat_final[j][5*i-2] = dat_final[j][5*i-2] / cuad
                dat_final[j][5*i-4] = degrees(atan2(dat_final[j][5*i-3], dat_final[j][5*i-2]))
                if dat_final[j][5*i-4] < 0:
                    dat_final[j][5*i-4] +=360
            else:
                dat_final[j][5*i-4] = None
            

            valores_numericos = []
            for valor in dat_boletin[j][5*i-1]:
                if valor is not None:  
                    try:
                        numero = float(valor)
                        valores_numericos.append(numero)
                    except ValueError:
                        continue
            if valores_numericos:
                valor_maximo = max(valores_numericos) 
                dat_final[j][5*i-1] = valor_maximo
            else:
                dat_final[j][5*i-1] = None

        
            valores_numericos = []
            for valor in dat_boletin[j][5*i]: 
                if valor is not None:  
                    try:
                        numero = float(valor)
                        valores_numericos.append(numero)
                    except ValueError:
                        continue
            if valores_numericos:
                suma_valores=sum(valores_numericos)
                media = suma_valores / len(valores_numericos)
                dat_final[j][5*i] = media
            else:
                dat_final[j][5*i] = None


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
            fila = [emission_time] + [valid_time] + [str(dat_final[j].get(k + 1, '')) for k in indices_validos]
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

    for i, seccion in secciones.items():
        (boletin_recortado[i], seccion) = generar_lineas(seccion, cod_boletin, i)
        seccion_dic.append(seccion)
    
    num_zonas, num_divisiones, div_por_zona, zona_de_la_division, nombre_division, nombre_zona = parametros_zonas_y_divisiones(cod_boletin)

    dic_boletin, procesar_zona = ordenar_lineas(seccion_dic, fecha, cod_boletin, num_zonas, num_divisiones) 

    for i in range(num_divisiones):    
        
        boletin_sep_fen[i] = separar_lineas_temporalmente(dic_boletin[i], fecha)

    boletin_sep_zona = ordenar_fenomenos_por_zonas(boletin_sep_fen, procesar_zona, cod_boletin, num_zonas, num_divisiones)
    
    for i in range(num_divisiones): 

        boletin_sep_temp[i] = ordenar_fenomenos_temporalmente(boletin_sep_zona[i], periodo)
        
        dat_boletin[i] = traducir(boletin_sep_temp[i])

        dat_final[i] = reducir_unico_valor_por_campo(dat_boletin[i])

        convertir_csv(dat_final[i], ruta_csv, fecha, periodo, nombre_zona, nombre_division, i)

    return boletin_recortado, dic_boletin, boletin_sep_fen, boletin_sep_zona, boletin_sep_temp, dat_boletin, dat_final
