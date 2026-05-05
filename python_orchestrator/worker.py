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
            "REGLA CRÍTICA DE CÓDIGO: Si tu tarea es escribir código, DEBES escribir la lógica 100% funcional y completa. NUNCA uses 'pass', 'TODO' ni funciones vacías.\n"
            "Para usar una herramienta, responde ÚNICAMENTE con este formato XML (NUNCA uses JSON):\n"
            "<tool_call>\n"
            "  <tool>nombre_herramienta</tool>\n"
            "  <args>argumento 1</args>\n"
            "  <args>argumento 2 (puedes poner código multilinea aquí sin problemas)</args>\n"
            "</tool_call>\n\n"
            f"Habilidades disponibles:\n{skills_context}\n\n"
            "REGLA DE ORO: Si en tu contexto ya ves una 'Observación' confirmando que la herramienta tuvo éxito, DETENTE. NO uses más herramientas. Responde resumiendo el éxito obtenido en lenguaje natural."
        )
        
        with console.status(f"[bold]> Worker [Intento {i+1}]...[/bold]", spinner="line"):
            response = await query_ollama(system_prompt, local_context, max_tokens=2048, temp=0.1)
            
        # Parsear XML en lugar de JSON
        match = re.search(r'<tool_call>(.*?)</tool_call>', response, re.DOTALL)
        if match:
            try:
                inner_xml = match.group(1)
                tool_match = re.search(r'<tool>(.*?)</tool>', inner_xml, re.DOTALL)
                args_matches = re.findall(r'<args>(.*?)</args>', inner_xml, re.DOTALL)
                
                if tool_match:
                    tool_name = tool_match.group(1).strip()
                    args = [arg.strip() for arg in args_matches]
                    
                    tool_call = {"tool": tool_name, "args": args}
                    console.print(f"[bold]> Ejecutando:[/bold] {tool_name}")
                    
                    observation = await execute_tool(tool_call)
                    console.print(f"[dim]  Observación: {observation}[/dim]")
                    
                    local_context += f"\nAcción: {json.dumps(tool_call)}\nObservación: {observation}"
                    continue
            except Exception as e:
                local_context += f"\nError al parsear XML: {e}"
                continue
        else:
            return response.strip()
            
    return "Worker abortado por límite de iteraciones."
