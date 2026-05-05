import sys
import os

if len(sys.argv) < 2:
    print("Error: Se requiere argumento: <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

try:
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        sys.exit(1)
        
    with open(file_path, "r") as f:
        content = f.read()
    print(f"Success:\n{content}")
except Exception as e:
    print(f"Error leyendo archivo: {e}")
