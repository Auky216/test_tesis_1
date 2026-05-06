import json
import re
from rich.console import Console
from llm_client import query_ollama
from tool_executor import execute_tool
from skills_manager import load_skills

console = Console()

async def run_worker(task: str, global_context: str) -> str:
    """
    Ejecuta una micro-tarea específica usando un mini-bucle ReAct.
    """
    max_loops = 3
    local_context = f"Contexto global de la operación:\n{global_context}\n\nTu tarea Específica AHORA es: {task}"
    
    for i in range(max_loops):
        skills_context = load_skills()
        system_prompt = (
            "Eres un Agente Trabajador (Worker). Tienes UNA sola tarea que cumplir.\n"
            "Si necesitas usar una herramienta, usa este formato XML:\n"
            "<tool>nombre_herramienta</tool>\n"
            "<args>primer_argumento</args>\n"
            "<args>segundo_argumento</args>\n\n"
            "EJEMPLO PARA ESCRIBIR CÓDIGO:\n"
            "Tarea: Escribir hola mundo en hola.py\n"
            "Respuesta:\n"
            "<tool>write_file</tool>\n"
            "<args>hola.py</args>\n"
            "<args>\nprint('Hola Mundo')\n</args>\n\n"
            "REGLA CRÍTICA: Todo el código debe estar dentro del segundo <args>. No uses 'pass'.\n"
            f"Habilidades disponibles:\n{skills_context}\n"
        )
        
        with console.status(f"[bold]> Worker [Intento {i+1}]...[/bold]", spinner="line"):
            response = await query_ollama(system_prompt, local_context, max_tokens=4096, temp=0.1)
            
        # 1. Extraer nombre de herramienta
        tool_match = re.search(r'<tool>(.*?)</tool>', response, re.DOTALL)
        if tool_match:
            tool_name = tool_match.group(1).strip()
            
            # 2. Extraer todos los bloques <args>
            args = [arg.strip().strip('"').strip("'") for arg in re.findall(r'<args>(.*?)</args>', response, re.DOTALL)]
            
            # 3. SMART FALLBACK AGRESIVO
            if tool_name == "write_file" and len(args) < 2:
                # Buscar bloque de código
                code_match = re.search(r'```(?:python|)?\s*(.*?)\s*```', response, re.DOTALL)
                if code_match:
                    args.append(code_match.group(1).strip())
                else:
                    # Buscar después de las etiquetas
                    parts = response.split('</args>')
                    potential = parts[-1].strip().strip('`').strip()
                    if len(potential) > 20:
                        args.append(potential)

            try:
                # Validar mínimos para write_file
                if tool_name == "write_file" and len(args) < 2:
                    console.print(f"[dim]  (Reintentando...) Falta el código en <args>.[/dim]")
                    local_context += "\nError: Olvidaste incluir el código dentro del segundo <args>. Inténtalo de nuevo con el código completo."
                    continue

                tool_call = {"tool": tool_name, "args": args}
                console.print(f"[bold]> Ejecutando:[/bold] {tool_name}")
                
                observation = await execute_tool(tool_call)
                
                # Normalizar resultado de "File exists"
                if "File exists" in observation:
                    observation = "Success (Directory already exists)"
                
                console.print(f"[dim]  Observación: {observation}[/dim]")
                
                # ✅ Si hubo éxito, terminar. Si falló, agregar al contexto y reintentar.
                if observation.startswith("Success") or "guardado en" in observation:
                    return f"Completado: {observation}"
                else:
                    local_context += f"\nAcción realizada: {tool_name}\nResultado (fallido): {observation}. Intenta de nuevo con un comando diferente."
                    continue
                    
            except Exception as e:
                console.print(f"[dim]  Error interno: {e}[/dim]")
                local_context += f"\nError interno: {e}"
                continue
        else:
            return response.strip()
            
    return "Worker agotó intentos sin completar la tarea."
