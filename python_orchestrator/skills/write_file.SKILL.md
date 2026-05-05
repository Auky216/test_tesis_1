Tool Name: write_file
Description: Escribe texto o código directamente en un archivo. Úsalo SIEMPRE que necesites crear scripts de Python, archivos de configuración o escribir código largo. NUNCA uses system_bash con echo para escribir código. Crea los directorios padre automáticamente si no existen.
Arguments:
- file_path (string): La ruta del archivo a crear/sobrescribir (ej. 'calculadora.py').
- content (string): El código o texto completo que se escribirá en el archivo.
