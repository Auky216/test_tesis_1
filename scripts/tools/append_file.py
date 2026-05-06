#!/usr/bin/env python3
"""
append_file: Añade contenido al final de un archivo existente.
Uso: python3 append_file.py <file_path> <content>
Si el archivo no existe, lo crea.
"""
import sys
import os

if len(sys.argv) < 3:
    print("Error: Se requieren argumentos: <file_path> <content>")
    sys.exit(1)

file_path = sys.argv[1]
content = sys.argv[2]

try:
    os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
    with open(file_path, "a") as f:
        f.write("\n" + content)
    abs_path = os.path.abspath(file_path)
    print(f"Success: Contenido añadido a: {abs_path}")
except Exception as e:
    print(f"Error al añadir a archivo: {e}")
