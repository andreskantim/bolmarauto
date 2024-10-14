#!/bin/bash

cod_periodo_boletin='FQXX43MM'
cd "../../datos/boletines/${cod_periodo_boletin}/bruto/"

# Primero, obtén una lista de fechas únicas de los archivos
fechas=$(ls *"${cod_periodo_boletin}".txt | cut -d'_' -f1 | sort | uniq)

for fecha in $fechas; do
    # Cuenta cuántos archivos existen para la fecha actual
    archivos_fecha=$(ls "${fecha}"_*"${cod_periodo_boletin}".txt | wc -l)

    # Comprueba si hay exactamente 2 archivos para la fecha
    if [ "$archivos_fecha" -ne 2 ]; then
        echo "La fecha $fecha no tiene exactamente 2 archivos, tiene $archivos_fecha."
    else
        # Si hay exactamente 2 archivos, comprueba sus horas específicas
        archivo_1200="${fecha}_1200_${cod_periodo_boletin}.txt"
        archivo_2000="${fecha}_2000_${cod_periodo_boletin}.txt"
        
        if [ ! -f "$archivo_1200" ]; then
            echo "Falta el archivo de las 12:00 para la fecha $fecha"
        fi
        
        if [ ! -f "$archivo_2000" ]; then
            echo "Falta el archivo de las 20:00 para la fecha $fecha"
        fi
    fi
done