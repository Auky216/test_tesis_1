import sys
import os

if len(sys.argv) < 3:
    print("Error: Se requieren argumentos: <file_path> <content>")
    sys.exit(1)

file_path = sys.argv[1]
content = " ".join(sys.argv[2:])

try:
    # Crear directorios si no existen
    dir_name = os.path.dirname(os.path.abspath(file_path))
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    with open(file_path, "w") as f:
        f.write(content)
    abs_path = os.path.abspath(file_path)
    print(f"Success: Archivo guardado en: {abs_path}")
except Exception as e:
    print(f"Error escribiendo archivo: {e}")
