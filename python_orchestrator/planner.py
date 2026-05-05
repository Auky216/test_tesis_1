import json
import re
from llm_client import query_ollama
from skills_manager import load_skills

async def generate_plan(user_input: str) -> list:
    skills = load_skills()
    system_prompt = (
        "Eres el Planificador (Planner) de un sistema Multi-Agente.\n"
        "Tu trabajo es analizar la petición del usuario y dividirla en una secuencia lógica de pasos técnicos accionables.\n"
        "IMPORTANTE: Los agentes trabajadores solo tienen acceso a estas herramientas:\n"
        f"{skills}\n\n"
        "Diseña los pasos asumiendo que usarán estas herramientas (ej. 'Usar system_bash para crear carpeta', 'Usar write_file para el código').\n"
        "RESPONDE ÚNICAMENTE CON UN ARREGLO JSON ESTRICTO (formato de lista de strings).\n"
        "Ejemplo:\n"
        "[\"Crear carpeta 'proyecto' con system_bash\", \"Escribir código en 'proyecto/main.py'\", \"Ejecutar test con system_bash\"]\n"
    )
    
    response = await query_ollama(system_prompt, user_input, max_tokens=1024, temp=0.1)
    
    match = re.search(r'\[.*\]', response.replace('\n', ''), re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return [user_input] # Fallback si falla
    return [user_input]
