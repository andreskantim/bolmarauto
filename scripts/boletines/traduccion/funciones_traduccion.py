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

def ordenar_claves(pattern, text):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.start() if match else float('inf')

def claves_zonas(valor, cod_boletin):
    if cod_boletin == "FQXX41MM":
        # ASTURIAS 44.01/7.02/43.50/-4.51,
        # CANTABRIA 43.84/-4.51/43.46/-3.16,
        # VIZCAYA 43.84/-3.16/43.46/-2.39,
        # GUIPUZCUA 43.84/-2.39/43.46/-1.70,
        dic = {
            1: "asturias",
            2: "cantabria",
            3: "vizcaya",
            4: "guipuzcua"
        }
    else:
        dic = {}

    return dic.get(valor)

def claves_ordenar_lineas(fenomeno):
    claves_neg = []
    claves = []

    if fenomeno == 1:
        claves_neg = [
            "MAR DE FONDO",
            "MARDE",
            "FONDO",
            "DEFONDO",
            "RIZADA",
            "MAREJADILLA",
            "MAREJADA",
            "FUERTE MAREJADA",
            "GRUESA",
            "MUY GRUESA",
            "ARBOLADA",
            "MONTAÑOSA",
            "ENORME",
            "VISIBILIDAD",
            "REGULAR",
            "MALA",
            "AGUACEROS",
            "TORMENTAS",
            "LLUVIA",
            "LLOVIZNA"
        ]

        claves = [
            r"(NORTE|SUR|ESTE|OESTE|SUROESTE|NOROESTE|SURESTE|NORESTE|N|S|E|W|NE|NW|SE|SW|VARIABLE).*?(o (NORTE|SUR|ESTE|OESTE|SUROESTE|NOROESTE|SURESTE|NORESTE|N|S|E|W|NE|NW|SE|SW|VARIABLE))?.*?(FUERZA)?.*?\d+.*?((a|o) \d+)?"
        ]

    elif fenomeno == 2:
        claves_neg = []
        claves = [
            "RIZADA",
            "MAREJADILLA",
            "MAREJADA",
            "FUERTE MAREJADA",
            "GRUESA",
            "MUY GRUESA",
            "ARBOLADA",
            "MONTANOSA",
            "ENORME"
        ]

    elif fenomeno == 3:
        claves_neg = []
        claves = [
            "MAR DE FONDO",
            "MARDE",
            "DEFONDO",
            "FONDO"
        ]

    elif fenomeno == 4:
        claves_neg = []
        claves = [
            "AGUACEROS",
            "TORMENTAS",
            "LLUVIA",
            "LLOVIZNA"
        ]

    elif fenomeno == 5:
        claves_neg = []
        claves = [
            "VISIBILIDAD",
            "REGULAR",
            "MALA"
        ]

    return claves_neg, claves

def claves_separar_lineas_temporalmente(fenomeno):

    claves = []

    if fenomeno == 1:
        claves = [
            r"TENDIENDO",
            r"Y\s*TENDIENDO",
            r"Y\s*TENDIENDO",
            r",\s*TENDIENDO",
            r"AMAINANDO",
            r"Y\s*AMAINANDO",
            r",\s*AMAINANDO",
            r"ARRECIANDO",
            r"Y\s*ARRECIANDO",
            r",\s*ARRECIANDO",
            r"TEMPORALMENTE",
            r"Y\s*TEMPORALMENTE",
            r",\s*TEMPORALMENTE",
            r"LOCALMENTE",
            r"Y\s*LOCALMENTE",
            r",\s*LOCALMENTE",
            r"OCASIONALMENTE",
            r"Y\s*OCASIONALMENTE",
            r",\s*OCASIONALMENTE",
            r"ROLANDO",
            r"Y\s*ROLANDO",
            r",\s*ROLANDO",
            r"QUEDANDO",
            r"Y\s*QUEDANDO",
            r",\s*QUEDANDO",
            r"SALVO",
            r"Y\s*SALVO",
            r",\s*SALVO",
            r"CON\s*AREAS",
            r", A \d+",
            "Y A ",
            " Y ",
            r",\s*\d+"
            #", ",
            #" y "
            # \w?
        ]

    elif fenomeno == 2:
        claves = [
            r"TENDIENDO",
            r"Y\s*TENDIENDO",
            r",\s*TENDIENDO",
            r"DISMINUYENDO",
            r"Y\s*DISMINUYENDO",
            r",\s*DISMINUYENDO",
            r"AUMENTANDO",
            r"Y\s*AUMENTANDO",
            r",\s*AUMENTANDO",
            r"TEMPORALMENTE",
            r"Y\s*TEMPORALMENTE",
            r",\s*TEMPORALMENTE",
            r"LOCALMENTE",
            r"Y\s*LOCALMENTE",
            r",\s*LOCALMENTE",
            r"OCASIONALMENTE",
            r"Y\s*OCASIONALMENTE",
            r",\s*OCASIONALMENTE",
            r"ROLANDO",
            r"Y\s*ROLANDO",
            r",\s*ROLANDO",
            r"QUEDANDO",
            r"Y\s*QUEDANDO",
            r",\s*QUEDANDO",
            r"SALVO",
            r"Y\s*SALVO",
            r",\s*SALVO",
            r"CON\s*AREAS",
            ", A ",
            "Y A ",
            " Y ",
            r",\s*\d+"
            #", ",
            #" y "
            # \w?
        ]

    elif fenomeno == 3:
        claves = [
            r"TENDIENDO",
            r"Y\s*TENDIENDO",
            r",\s*TENDIENDO",
            r"DISMINUYENDO",
            r"Y\s*DISMINUYENDO",
            r",\s*DISMINUYENDO",
            r"AUMENTANDO",
            r"Y\s*AUMENTANDO",
            r",\s*AUMENTANDO",
            r"TEMPORALMENTE",
            r"Y\s*TEMPORALMENTE",
            r",\s*TEMPORALMENTE",
            r"LOCALMENTE",
            r"Y\s*LOCALMENTE",
            r",\s*LOCALMENTE",
            r"OCASIONALMENTE",
            r"Y\s*OCASIONALMENTE",
            r",\s*OCASIONALMENTE",
            r"ROLANDO",
            r"Y\s*ROLANDO",
            r",\s*ROLANDO",
            r"QUEDANDO",
            r"Y\s*QUEDANDO",
            r",\s*QUEDANDO",
            r"SALVO",
            r"Y\s*SALVO",
            r",\s*SALVO",
            r"CON\s*AREAS",
            ", A ",
            "Y A ",
            " Y ",
            r",\s*\d+"
            #", ",
            #" y "
            # \w?
        ]

    elif fenomeno == 4:
        claves = []

    elif fenomeno == 5:
        claves = []

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

def claves_traduccion(valor, fenomeno, variable, funcion):
    if fenomeno == 1:
        if variable == 1:
            dic = {
                r"(NORTE|N)\s*(O|Y|A)\s*(NOROESTE|NW)": 337.5,
                r"(NOROESTE|NW)\s*(O|Y|A)\s*(NORTE|N)": 337.5,
                r"(NOROESTE|NW)\s*(O|Y|A)\s*(OESTE|W)": 292.5,
                r"(OESTE|W)\s*(O|Y|A)\s*(NOROESTE|NW)": 292.5,
                r"(OESTE|W)\s*(O|Y|A)\s*(SUROESTE|SW)": 247.5,
                r"(SUROESTE|SW)\s*(O|Y|A)\s*(OESTE|W)": 247.5,
                r"(SUROESTE|SW)\s*(O|Y|A)\s*(SUR|S)": 202.5,
                r"(SUR|S)\s*(O|Y|A)\s*(SUROESTE|SW)": 202.5,
                r"(SUR|S)\s*(O|Y|A)\s*(SURESTE|SE)": 157.5,
                r"(SURESTE|SE)\s*(O|Y|A)\s*(SUR|S)": 157.5,
                r"(SURESTE|SE)\s*(O|Y|A)\s*(ESTE|E)": 112.5,
                r"(ESTE|E)\s*(O|Y|A)\s*(SURESTE|SE)": 112.5,
                r"(ESTE|E)\s*(O|Y|A)\s*(NORESTE|NE)": 67.5,
                r"(NORESTE|NE)\s*(O|Y|A)\s*(ESTE|E)": 67.5,
                r"(NORESTE|NE)\s*(O|Y|A)\s*(NORTE|N)": 22.5,
                r"(NORTE|N)\s*(O|Y|A)\s*(NORESTE|NE)": 22.5,
                r"(NORTE|N|COMPONENTE\s*N)": 0,
                r"(NOROESTE|NW)": 315,
                r"(NORESTE|NE)": 45,
                r"(SUR|S|COMPONENTE\s*S)": 180,
                r"(SUROESTE|SW)": 225,
                r"(SURESTE|SE)": 135,
                r"(OESTE|W|COMPONENTE\s*W)": 270,
                r"(ESTE|E|COMPONENTE\s*E)": 90,
                "VARIABLE": "X"
            }
        elif variable == 2:
            dic = {
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
            dic = {
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
                #"NO_CLAVE": "X"
            }
    
    elif fenomeno == 2:
        if variable == 1:
            dic = {}
        elif variable == 2:
            dic = {
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
                #"NO_CLAVE": 1.5
            }
        elif variable == 3:
            dic = {
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
                #"NO_CLAVE": 1
            }

    elif fenomeno == 3:
        if variable == 1:
            dic = {
                r"(NORTE|N)\s*(O|Y|A)\s*(NOROESTE|NW)": 337.5,
                r"(NOROESTE|NW)\s*(O|Y|A)\s*(NORTE|N)": 337.5,
                r"(NOROESTE|NW)\s*(O|Y|A)\s*(OESTE|W)": 292.5,
                r"(OESTE|W)\s*(O|Y|A)\s*(NOROESTE|NW)": 292.5,
                r"(OESTE|W)\s*(O|Y|A)\s*(SUROESTE|SW)": 247.5,
                r"(SUROESTE|SW)\s*(O|Y|A)\s*(OESTE|W)": 247.5,
                r"(SUROESTE|SW)\s*(O|Y|A)\s*(SUR|S)": 202.5,
                r"(SUR|S)\s*(O|Y|A)\s*(SUROESTE|SW)": 202.5,
                r"(SUR|S)\s*(O|Y|A)\s*(SURESTE|SE)": 157.5,
                r"(SURESTE|SE)\s*(O|Y|A)\s*(SUR|S)": 157.5,
                r"(SURESTE|SE)\s*(O|Y|A)\s*(ESTE|E)": 112.5,
                r"(ESTE|E)\s*(O|Y|A)\s*(SURESTE|SE)": 112.5,
                r"(ESTE|E)\s*(O|Y|A)\s*(NORESTE|NE)": 67.5,
                r"(NORESTE|NE)\s*(O|Y|A)\s*(ESTE|E)": 67.5,
                r"(NORESTE|NE)\s*(O|Y|A)\s*(NORTE|N)": 22.5,
                r"(NORTE|N)\s*(O|Y|A)\s*(NORESTE|NE)": 22.5,
                r"(NORTE|N|COMPONENTE\s*N)": 0,
                r"(NOROESTE|NW)": 315,
                r"(NORESTE|NE)": 45,
                r"(SUR|S|COMPONENTE\s*S)": 180,
                r"(SUROESTE|SW)": 225,
                r"(SURESTE|SE)": 135,
                r"(OESTE|W|COMPONENTE\s*W)": 270,
                r"(ESTE|E|COMPONENTE\s*E)": 90,
                "VARIABLE": "X",
                #"NO_CLAVE": "X"
            }
        elif variable == 2:
            dic = {
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
            dic = {
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
            dic = {}
        elif variable == 2:
            dic = {}
        elif variable == 3:
            dic = {}
    elif fenomeno == 5:
        if variable == 1:
            dic = {}
        elif variable == 2:
            dic = {}
        elif variable == 3:
            dic = {}

    if funcion == 1: #Traduccion
        return dic.get(valor)
    elif funcion == 2:
        return dic #Enumeracion

def generar_lineas(boletin_recortado, seccion, cod_boletin, i): 
    
    seccion = re.sub(r'(\.)(?!\s*$)', r'\1\n', seccion) # Añadir salto de línea después de cada punto y eliminar espacio al principio de la línea siguiente
    seccion = re.sub(r'(?<!\.)\n', '', seccion) # Eliminar saltos de línea donde no hay punto final
    seccion = re.sub(r'^\s+', '', seccion, flags=re.MULTILINE) # Eliminar espacios al principio de cada línea
    seccion = re.sub(r'^(.*?):', '', seccion)# Eliminar aguas costeras y el nombre de la región en el encabezado de cada sección
    boletin_recortado += f"{claves_zonas(i, cod_boletin)}\n{seccion}\n"# Formatear la sección con el identificador de zona y contenido modificado

    return boletin_recortado, seccion

def ordenar_lineas(seccion): 
    
    dic_boletin = {i: [] for i in range(1, 6)}
    lineas = seccion.split('\n')

    for i in range(1, 6):
        for linea in lineas:
            negado = False
            claves_neg, claves = claves_ordenar_lineas(i)
            for clave_neg in claves_neg:
                if re.findall(clave_neg, linea, re.IGNORECASE):
                    negado = True
                    break
            if negado:
                continue 
            
            coincide = False
            for clave in claves:
                if re.findall(clave, linea, re.IGNORECASE):
                    coincide = True
                    break
            if coincide:
                dic_boletin[i].append(linea.strip())

    return dic_boletin

def separar_lineas_temporalmente(dic_boletin):
    
    temp_boletin = {i: [] for i in range(1, 6)}

    for i in range(1,6):# hasta 6
        
        divisores_ord = claves_separar_lineas_temporalmente(i)
        encontrado_divisor=True
        
        for fenomeno in dic_boletin[i]:
            divisor = None
            while encontrado_divisor:
                
                divisores_ord = sorted(divisores_ord, key=lambda orden: ordenar_claves(orden, fenomeno))
                encontrado_divisor = False
                if divisores_ord and re.search(divisores_ord[0], fenomeno, re.IGNORECASE):
                    partes = re.split(f'({divisores_ord[0]})', fenomeno, 1, flags=re.IGNORECASE)
                    encontrado_divisor = True
                    fenomeno = partes[2]
                    other = partes[0]
                    if divisor: 
                        temp_boletin[i].append(divisor + other)
                    else:
                        temp_boletin[i].append(other)
                    divisor = partes[1]

            if divisor: 
                fenomeno   
                temp_boletin[i].append(divisor + fenomeno)
            else:
                temp_boletin[i].append(fenomeno)
            
    return temp_boletin

def ordenar_fenomenos_temporalmente(temp_boletin, periodo):

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
                
                if re.search('DURANTE', fenomeno, re.IGNORECASE):#1 STEP ALANTE DEL FENOMENO, SOLO ESOS
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

def traduccion(dic_boletin):
    
    dat_boletin={}

    for j in range(0, 9):
        dat_boletin[j] = {i: [] for i in range(1, 26)} 
    
    for i in range(1,6):

        clave_ang_0=False
        clave_max_0=False
        clave_med_0=False

        for j in range (0,9):

            claves_trad_1 = claves_traduccion(None, i, 1, 2)
            claves_trad_2 = claves_traduccion(None, i, 2, 2)
            claves_trad_3 = claves_traduccion(None, i, 3, 2)

            clave_ang=False
            clave_max=False
            clave_med=False

            total_fenomenos = len(dic_boletin[j][i])
            for idx, fenomeno in enumerate(dic_boletin[j][i]):

                for clave in claves_trad_1:    
                    pat_clave =  r'\b' + clave + r'\b'
                    if re.search(pat_clave, fenomeno, re.IGNORECASE):#usar match
                        try:
                            valor_numerico = float(claves_traduccion(clave, i, 1, 1))
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
                        if j==0:
                            clave_ang_0=True
                        else:
                            clave_ang=True       
                        break   
                
                for clave in claves_trad_2:  
                    pat_clave = r'\b' + clave + r'\b'  
                    if re.search(clave, fenomeno, re.IGNORECASE):
                        dat_boletin[j][i * 5 - 1].append(claves_traduccion(clave, i, 2, 1))
                        if j==0:
                            clave_max_0=True
                        else:
                            clave_max=True  
                        break   
                
                for clave in claves_trad_3:    
                    pat_clave = r'\b' + clave + r'\b'
                    if re.search(clave, fenomeno, re.IGNORECASE):
                        dat_boletin[j][i * 5].append(claves_traduccion(clave, i, 3, 1))
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
                dat_boletin[j][i*5 - 4].append(claves_traduccion("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 - 3] == []:
                dat_boletin[j][i*5 - 3].append(claves_traduccion("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 - 2] == []:
                dat_boletin[j][i*5 - 2].append(claves_traduccion("NO_CLAVE", i, 1, 1))
            if dat_boletin[j][i*5 - 1] == []:
                dat_boletin[j][i*5 - 1].append(claves_traduccion("NO_CLAVE", i, 2, 1))
            if dat_boletin[j][i*5] == []:
                dat_boletin[j][i*5].append(claves_traduccion("NO_CLAVE", i, 3, 1))

    return dat_boletin

def reducir_unico_valor_por_campo(dat_boletin):
    
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

def convertir_csv(dat_final, ruta_csv, cod_boletin, fecha, periodo, i):

    nombre_archivo = f'{claves_zonas(i, cod_boletin)}.csv'  
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

def funcion_principal(nombre_archivo, cod_boletin, ruta_csv): 
    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()

    secciones = {}
    dic_boletin = {}
    temp_boletin = {}
    boletin_sep_temp = {}
    dat_boletin = {}
    dat_final = {}

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

    for i, match in enumerate(matches, start=1): 
        secciones[i] = match.group(1)

    boletin_recortado = fecha + '\n\n' # Preparar el texto de salida

    for i, seccion in secciones.items():

        (boletin_recortado, seccion) = generar_lineas(boletin_recortado, seccion, cod_boletin, i)
  
        dic_boletin[i] = ordenar_lineas(seccion)
        
        (temp_boletin[i]) = separar_lineas_temporalmente(dic_boletin[i])
    # for i, seccion in secciones.items():
        boletin_sep_temp[i] = ordenar_fenomenos_temporalmente(temp_boletin[i], periodo)
        
        dat_boletin[i] = traduccion(boletin_sep_temp[i])

        dat_final[i] = reducir_unico_valor_por_campo(dat_boletin[i])

        convertir_csv(dat_final[i], ruta_csv, cod_boletin, fecha, periodo, i)
    
        
    #print(dat_final[4][8][5])

    return boletin_recortado, dic_boletin, temp_boletin, boletin_sep_temp, dat_boletin, dat_final
