#!/bin/bash

#SBATCH --error=errores/err_%j.txt


# #SBATCH -c 32
# #SBATCH -t 02:30:00
# #SBATCH --mem=16GB
# #SBATCH --output=salidas/res_%j.txt
# #SBATCH --exclusive

# source $STORE/miniconda3/envs/genhpc/bin/activate

# Inicializa Conda
source $STORE/miniconda3/etc/profile.d/conda.sh

# Activa entorno Conda
conda activate genhpc

# Ejecuta el script python pasado como argumento
python "$1"

#python ../sk_learn/TREE.py

#python ../predicciones/prediccion.py
