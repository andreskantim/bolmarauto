#!/bin/bash

#Actualiza el git del directorio ecmwf

# Mejor descripción del commit como argumento
if [ $# -eq 0 ]; then
    echo "Uso: $0 <mensaje del commit>"
    exit 1
fi

# Directorio del repositorio de Git
REPO_DIR="/home/andreskantim/ecmwf/scripts"

# Cambiar al directorio del repositorio
cd "$REPO_DIR"

# Verificar si el cambio de directorio fue exitoso
if [ $? -ne 0 ]; then
    echo "Error al cambiar al directorio $REPO_DIR"
    exit 1
fi

# Verificar el estado del repositorio primero
git status

# Añadir cambios al área de preparación
git add -A

# Crear un commit con un mensaje descriptivo
git commit -m "$1"

# Empujar los cambios a la rama main
git push -u origin main