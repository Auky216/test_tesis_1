from rich.console import Console
from planner import generate_plan
from worker import run_worker
from llm_client import query_ollama

console = Console()

async def run_agent(user_input: str, historial: str) -> str:
    """
    Arquitectura Plan-and-Execute.
    """
    console.print("\n[bold]> Generando plan de ejecución...[/bold]")
    plan = await generate_plan(user_input)
    
    console.print(f"[dim]Plan generado:[/dim]\n" + "\n".join([f"  - {t}" for t in plan]))
    
    global_context = f"Historial de chat:\n{historial}\n\nPetición del usuario: {user_input}\n\nResultados parciales de las tareas ejecutadas:\n"
    
    for idx, task in enumerate(plan):
        console.print(f"\n[bold]> [Tarea {idx+1}/{len(plan)}][/bold] {task}")
        worker_result = await run_worker(task, global_context)
        console.print(f"[bold]  [Completado][/bold] {worker_result}")
        
        global_context += f"- Tarea: {task}\n  Resultado: {worker_result}\n\n"
        
    console.print("\n[bold]> Sintetizando reporte final...[/bold]")
    synth_prompt = (
        "Eres el Synthesizer final (Orquestador Maestro). Lee la petición original del usuario y el contexto que contiene los resultados de todas las tareas ejecutadas por tus agentes trabajadores.\n"
        "Redacta una respuesta final humana, clara y concisa al usuario, resumiendo lo que se logró. No menciones a los 'agentes trabajadores' ni tu proceso interno, solo háblale al usuario directamente."
    )
    
    with console.status("[bold]Consolidando datos...[/bold]", spinner="line"):
        final_response = await query_ollama(synth_prompt, global_context, max_tokens=2048, temp=0.6)
    
    return final_response.strip()
