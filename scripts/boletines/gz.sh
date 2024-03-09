#!/bin/bash

# Directorio donde se encuentran los archivos .tar y .gz
directorio="/home/andreskantim/ecmwf/datos/boletines"

#Codigo del boletin
codigo_boletin="FQXX41MM"

#Archivo comprimido
nombre_tar="Boletines_201501.tar"

# Directorio destino donde se guardarán los archivos descomprimidos y renombrados
directorio_destino="${directorio}/${codigo_boletin}"

# Verifica si el directorio destino existe, si no, lo crea
if [ ! -d "$directorio_destino" ]; then
    mkdir -p "$directorio_destino"
fi

# Extrae los archivos del .tar directamente en el directorio destino
tar -xvf "${directorio}/${nombre_tar}" -C "$directorio_destino"

# Cambia al directorio destino para trabajar con los archivos descomprimidos
cd "$directorio_destino" || exit 1

# Para cada archivo .gz en el directorio destino
for archivo in *.gz; do
    # Extrae la fecha y el código (567 o 569) del nombre del archivo
    fecha=$(echo $archivo | cut -d'_' -f1)
    codigo=$(echo $archivo | grep -o -E '567|569')

    # Decide el sufijo según el código
    if [[ $codigo == "569" ]]; then
        sufijo="1200"
    elif [[ $codigo == "567" ]]; then
        sufijo="2000"
    else
        sufijo="0000" # Por si acaso hay algún archivo que no cumpla
    fi

    # Construye el nuevo nombre del archivo sin la compresión .gz
    nuevo_nombre="${fecha}_${sufijo}_${codigo_boletin}.txt"

    # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
    gunzip -c "$archivo" > "$nuevo_nombre"

    echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

    # Elimina el archivo .gz original si deseas mantener solo la versión descomprimida
    rm "$archivo"
done