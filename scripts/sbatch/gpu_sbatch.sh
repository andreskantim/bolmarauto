#!/bin/bash

#SBATCH --nodes=1               # Esto necesita coincidir con Fabric(num_nodes=...)
#SBATCH --ntasks-per-node=1     # Esto necesita coincidir con Fabric(devices=...)
#SBATCH --gres=gpu:a100:1       # Solicitar N GPUs por máquina
#SBATCH --mem=32G               # Solicitar 32 GB por nodo
#SBATCH -c 32                   # Solicitar 32 núcleos por nodo (total 64 núcleos)
#SBATCH --time=00:30:00         # Tiempo máximo de ejecución
#SBATCH --output=salidas/resultado_%j.txt
#SBATCH --error=salidas/error_%j.txt

# Cargar módulos necesarios
#module load python/3.8
#module load cuda/11.0

source $STORE/mytorchdist/bin/activate

python ../sk_learn/gpu_sk_learn.py

sstat -j $SLURM_JOB_ID.batch