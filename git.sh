#!/bin/bash

# Mejor descripción del commit como argumento
if [ $# -eq 0 ]; then
    echo "Uso: $0 <mensaje del commit>"
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