import json
import re
from llm_client import query_ollama
from skills_manager import load_skills

async def generate_plan(user_input: str) -> list:
    skills = load_skills()
    system_prompt = (
        "Eres el Planificador (Planner) de un sistema Multi-Agente que trabaja con un LLM pequeño (3B parámetros).\n"
        "El LLM tiene un límite de ~300 líneas de código por llamada. Por eso, para tareas de código complejo, DEBES dividir.\n\n"
        "REGLAS DE CHUNKING (División de Código):\n"
        "1. Para código SIMPLE (<50 líneas): Un solo paso 'write_file'.\n"
        "2. Para código MEDIANO (50-150 líneas): Dos pasos — write_file para la base, append_file para el resto.\n"
        "3. Para código COMPLEJO (>150 líneas, ej. árboles, grafos, algoritmos de ordenamiento): Divide por COMPONENTE LÓGICO:\n"
        "   - Paso A: write_file con clases base, constantes e imports.\n"
        "   - Paso B: append_file con el primer grupo de métodos (ej. rotaciones, búsqueda).\n"
        "   - Paso C: append_file con el segundo grupo (ej. inserción con fixup).\n"
        "   - Paso D: append_file con el tercer grupo (ej. eliminación con fixup).\n"
        "   - Paso E: validate_python para verificar que el archivo no tenga 'pass' ni errores.\n"
        "   - Paso F: system_bash para ejecutar y testear.\n\n"
        "4. SIEMPRE añade un paso de 'validate_python' antes del test final.\n"
        "5. Si el validate_python falla, el sistema reintentará automáticamente ese chunk.\n\n"
        f"Herramientas disponibles: {skills}\n\n"
        "RESPONDE ÚNICAMENTE CON UN ARREGLO JSON ESTRICTO.\n"
        "Ejemplo para Red-Black Tree:\n"
        "[\"Crear carpeta con system_bash\","
        " \"write_file: clase Node y NIL centinela en rbt/rbt.py\","
        " \"append_file: métodos _rotate_left y _rotate_right en rbt/rbt.py\","
        " \"append_file: método insert y _fix_insert en rbt/rbt.py\","
        " \"append_file: método delete y _fix_delete en rbt/rbt.py\","
        " \"append_file: inorder_traversal y bloque __main__ en rbt/rbt.py\","
        " \"validate_python rbt/rbt.py\","
        " \"system_bash: python3 rbt/rbt.py\"]\n"
    )

    response = await query_ollama(system_prompt, user_input, max_tokens=1024, temp=0.1)

    match = re.search(r'\[.*\]', response.replace('\n', ''), re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return [user_input]
    return [user_input]
