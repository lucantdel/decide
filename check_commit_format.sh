#!/bin/bash

# Obtener el mensaje de commit más reciente
commit_message=$(git log --format=%B -n 1 HEAD)

# Verificar si el mensaje de commit sigue el formato esperado o es un mensaje de fusión
if [[ $commit_message =~ ^(feat|fix|research|refactor|docs|test|conf): ]] || [[ $commit_message =~ ^Merge ]]; then
    echo "El formato de commit es correcto."
else
    echo "Error: El mensaje de commit no cumple con el formato esperado."
    echo "Mensaje de commit problemático: '$commit_message'"
    exit 1
fi
