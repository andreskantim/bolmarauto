#!/bin/bash

#En caso de boletines correciones, se queda con el de hora mas tardia.


# Directorio donde se encuentran los archivos .tar y .gz
directorio="../../datos/boletines/tar"

#Codigo del boletin
codigo_boletin="FQXX43MM"

#Archivo comprimido
nombre_tar="${codigo_boletin}.tar"

FECHA_LIMITE="20151217"


# Directorio destino donde se guardarán los archivos descomprimidos y renombrados

directorio_destino="../../datos/boletines/${codigo_boletin}/bruto"

# Verifica si el directorio destino existe, si no, lo crea
if [ ! -d "$directorio_destino" ]; then
    mkdir -p "$directorio_destino"
fi

rm -rf "${directorio_destino:?}"/*

# Extrae los archivos del .tar directamente en el directorio destino
tar -xvf "${directorio}/${nombre_tar}" -C "$directorio_destino"

# Cambia al directorio destino para trabajar con los archivos descomprimidos
cd "$directorio_destino" || exit 1


for archivo in *.gz; do

    # Extrae la fecha del nombre del archivo
    fecha=$(echo "$archivo" | cut -d'_' -f1)
    
    # Compara si la fecha del archivo es menor o igual a la fecha límite
    if [[ "$archivo" == *"20160930_0703"* && "$codigo_boletin" == "FQXX40MM" ]]; then
            # Construye el nuevo nombre del archivo
        nuevo_nombre="20160929_2000_FQXX40MM.txt"
            # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        # Elimina el archivo .gz original si deseas mantener solo la versión descomprimida
        rm "$archivo"

    elif [[ "$archivo" == *"20160930_0703"* && "$codigo_boletin" == "FQXX41MM" ]]; then
            # Construye el nuevo nombre del archivo
        nuevo_nombre="20160929_2000_FQXX41MM.txt"
            # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        # Elimina el archivo .gz original si deseas mantener solo la versión descomprimida
        rm "$archivo"

    elif [[ "$archivo" == *"20160930_0703"* && "$codigo_boletin" == "FQXX42MM" ]]; then
            # Construye el nuevo nombre del archivo
        nuevo_nombre="20160929_2000_FQXX42MM.txt"
            # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        # Elimina el archivo .gz original si deseas mantener solo la versión descomprimida
        rm "$archivo"

    elif [[ "$archivo" == *"20160930_0703"* && "$codigo_boletin" == "FQXX43MM" ]]; then
            # Construye el nuevo nombre del archivo
        nuevo_nombre="20160929_2000_FQXX43MM.txt"
            # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        # Elimina el archivo .gz original si deseas mantener solo la versión descomprimida
        rm "$archivo"

    elif [[ "$archivo" == *"20171204_1809"* && "$codigo_boletin" == "FQXX43MM" ]]; then
            # Construye el nuevo nombre del archivo
        nuevo_nombre="20171204_1200_FQXX43MM.txt"
            # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        nuevo_nombre="20171204_2000_FQXX43MM.txt"
            # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        # Elimina el archivo .gz original si deseas mantener solo la versión descomprimida
        rm "$archivo"
        
    elif [[ "$archivo" == *"20231230_1426"* && "$codigo_boletin" == "FQXX43MM" ]]; then
            # Construye el nuevo nombre del archivo
        nuevo_nombre="20231230_1200_FQXX43MM.txt"
            # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        # Elimina el archivo .gz original si deseas mantener solo la versión descomprimida
        rm "$archivo"
        
    
    elif [[ "$fecha" < "$FECHA_LIMITE" ]]; then
        # echo "Procesando $archivo, fecha menor que $FECHA_LIMITE"
        # Extrae la fecha y el código (567 o 569) del nombre del archivo
        fecha=$(echo $archivo | cut -d'_' -f1)
        codigo=$(echo $archivo | grep -o -E '567|569' | head -n 1)

        # Decide el sufijo según el código
        if [[ $codigo == "569" ]]; then
        sufijo="1200"
        elif [[ $codigo == "567" ]]; then
        sufijo="2000"
        else
        sufijo="0000" # Por si acaso hay algún archivo que no cumpla
        fi
        
        nuevo_nombre="${fecha}_${sufijo}_${codigo_boletin}.txt"
        

        # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        # Elimina el archivo .gz original si deseas mantener solo la versión descomprimida
        rm "$archivo"


    else
        # echo "Procesando $archivo, fecha mayor o igual que $FECHA_LIMITE"

         # Extrae la fecha y hora del nombre del archivo
        fecha=$(echo $archivo | cut -d'_' -f1)
        hora=$(echo $archivo | cut -d'_' -f2)

        # Decide el nuevo valor de la hora basado en si es mayor o menor a 1400
        if [[ "$hora" < "1400" ]]; then
            nueva_hora="1200"
        else
            nueva_hora="2000"
        fi

        # Construye el nuevo nombre del archivo sin la compresión .gz y sin el identificador único
        nuevo_nombre="${fecha}_${nueva_hora}_${codigo_boletin}.txt"

        # Descomprime el archivo manteniendo el original (.gz) y lo guarda con el nuevo nombre
        gunzip -c "$archivo" > "$nuevo_nombre"

        echo "Descomprimido y renombrado: $archivo a $nuevo_nombre"

        #Si deseas eliminar el archivo .gz original, descomenta la siguiente línea
        rm "$archivo"
    fi
done        

