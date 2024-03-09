#!/bin/bash

tar -xvf Boletines_201501.tar
# Directorio donde se encuentran los archivos .gz
directorio="/home/andreskantim/ecmwf/salidas/boletines"

# Cambia al directorio especificado
cd "$directorio"

# Para cada archivo .gz en el directorio actual
for archivo in *.gz; do
    # Extrae la fecha y el código (567 o 569) del nombre del archivo
    fecha=$(echo $archivo | cut -d'_' -f1)
    codigo=$(echo $archivo | grep -o -E '567|569')

    # Decide el sufijo según el código
    if [[ $codigo == "569" ]]; then
        sufijo="_1200"
    elif [[ $codigo == "567" ]]; then
        sufijo="_2000"
    else
        sufijo="_0000" # Por si acaso hay algún archivo que no cumpla
    fi

    # Incluye el valor FQXX41MM en el nuevo nombre
    valor="FQXX41MM"

    # Construye el nuevo nombre del archivo sin la compresión .gz
    nuevo_nombre="${fecha}${sufijo}_${valor}.txt"

    # Descomprime el archivo manteniendo el original (.gz)
    gunzip -c $archivo > "$nuevo_nombre"

    echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

    rm $archivo
done