#!/bin/bash

#SBATCH -c 32 #(5 cores per job)
#SBATCH -t 01:00:00 #(10 min of execution time)
#SBATCH --output=salidas/resultado_%j.txt
#SBATCH --error=salidas/error_%j.txt
#SBATCH --mem=16GB #(4GB of memory)
##SBATCH --exclusive

source $STORE/mytorchdist/bin/activate

python ../sk_learn/sk_learn.py

python ../predicciones/prediccion.py