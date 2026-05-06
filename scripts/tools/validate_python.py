#!/usr/bin/env python3
"""
validate_python: Valida que un archivo Python sea sintácticamente correcto
y no contenga métodos vacíos con 'pass'.
Uso: python3 validate_python.py <file_path>
"""
import sys
import ast
import os

if len(sys.argv) < 2:
    print("Error: Se requiere: <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

if not os.path.exists(file_path):
    print(f"Error: Archivo no encontrado: {file_path}")
    sys.exit(1)

with open(file_path, "r") as f:
    source = f.read()

# 1. Validar sintaxis
try:
    tree = ast.parse(source)
except SyntaxError as e:
    print(f"INVALID: Error de sintaxis en línea {e.lineno}: {e.msg}")
    sys.exit(1)

# 2. Detectar funciones/métodos vacíos (solo tienen 'pass' o docstring + pass)
issues = []
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        body = node.body
        # Ignorar docstrings, buscar si el cuerpo real es solo Pass
        real_body = [n for n in body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant))]
        if all(isinstance(n, ast.Pass) for n in real_body) and real_body:
            issues.append(f"  - Función vacía: '{node.name}' (línea {node.lineno})")

if issues:
    print(f"INCOMPLETE: El archivo tiene {len(issues)} función(es) sin implementar:")
    for issue in issues:
        print(issue)
    sys.exit(1)

print(f"OK: {file_path} es válido y completo. ({len(list(ast.walk(tree)))} nodos AST)")
