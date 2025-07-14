#!/bin/bash

# Lista de regresores
#regresores=("tree" "svr" "rna" "kn")
regresores=("TFM2")

# Script base de SLURM
slurm_script="cpu_sbatch.sh"

# Parámetros que quieres modificar
NUCLEOS="32"        # Número de nucleos (ej: 32)
MEMORIA="32GB"    # Memoria por nodo (ej: 16G)
TIEMPO="12:00:00" # Tiempo máximo de ejecución (ej: 2 horas)

# Verificación de existencia del script sbatch
if [ ! -f "$slurm_script" ]; then
  echo "Error: no se encuentra el archivo $slurm_script"
  exit 1
fi

# Iterar sobre cada tipo de regresor
for reg in "${regresores[@]}"; do
  ruta_scripts="../sk_learn/${reg}"
  # ruta_scripts="../sk_learn/${reg}/scripts"
  ruta_resultados="../sk_learn/${reg}/resultados"

  # Crear carpeta de resultados si no existe
  mkdir -p "$ruta_resultados"

  # Iterar sobre cada .py en la carpeta
  for pyfile in "$ruta_scripts"/*.py; do
    if [ -f "$pyfile" ]; then
      nombre_archivo=$(basename "$pyfile" .py)
      salida="${ruta_resultados}/${nombre_archivo}_%j.txt"

      echo "Enviando $pyfile con salida $salida"
      
      sbatch --output="$salida" \
             --cpus-per-task=$NUCLEOS \
             --mem=$MEMORIA \
             --time=$TIEMPO \
             "$slurm_script" "$pyfile"
    fi
  done
done