#!/bin/bash
# Script para verificar instalación de bwrap y preparar el entorno
if ! command -v bwrap &> /dev/null
then
    echo "bubblewrap no está instalado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y bubblewrap
fi

echo "bwrap disponible. Los entornos aislados se construirán dinámicamente en execution_tool.py"
