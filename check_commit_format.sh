#!/bin/bash

# Obtener los mensajes de commit desde el último push
commit_messages=$(git log --format=%B -n 1 HEAD)

# Verificar si el mensaje de commit sigue el formato
if [[ $commit_messages =~ ^(feat|fix|research|refactor|docs|test|conf): ]]; then
    echo "El formato de commit es correcto."
else
    echo "Error: Los mensajes de commit no cumplen con el formato esperado."
    exit 1
fi
