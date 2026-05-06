import os
from rich.console import Console
from rich.rule import Rule
from planner import generate_plan
from worker import run_worker
from llm_client import query_ollama

# Mostrar logs internos solo si se pide explícitamente
VERBOSE = os.environ.get("RASPIA_VERBOSE", "0") == "1"

console = Console()

MAX_VALIDATION_RETRIES = 2

async def run_agent(user_input: str, historial: str) -> str:
    """
    Arquitectura Plan-and-Execute con Validation Loop.
    Si un paso de validate_python falla, reintenta el chunk anterior.
    """
    if VERBOSE:
        console.print("\n[bold]> Generando plan de ejecución...[/bold]")
    plan = await generate_plan(user_input)

    if VERBOSE:
        console.print(f"[dim]Plan generado:[/dim]\n" + "\n".join([f"  - {t}" for t in plan]))

    global_context = (
        f"Historial de chat:\n{historial}\n\n"
        f"Petición del usuario: {user_input}\n\n"
        f"Resultados parciales:\n"
    )

    last_write_task = None   # Guarda el último chunk escrito para poder reintentarlo
    idx = 0

    while idx < len(plan):
        task = plan[idx]
        if VERBOSE:
            console.print(f"\n[bold]> [Tarea {idx+1}/{len(plan)}][/bold] {task}")

        # ── Detectar si esta tarea es una validación ──────────────────
        is_validation = any(kw in task.lower() for kw in ["validate_python", "validar", "validate"])

        worker_result = await run_worker(task, global_context)

        # ── Si es validación y FALLÓ → reintentar el chunk anterior ──
        if is_validation and ("INCOMPLETE" in worker_result or "INVALID" in worker_result or "Error" in worker_result):
            if VERBOSE:
                console.print(f"[bold]  [Validación FALLIDA][/bold] {worker_result}")

            if last_write_task and "_retry_count" not in last_write_task:
                for retry in range(1, MAX_VALIDATION_RETRIES + 1):
                    if VERBOSE:
                        console.print(f"\n[bold]  > Reintento {retry}/{MAX_VALIDATION_RETRIES}: Re-escribiendo chunk...[/bold]")
                    retry_result = await run_worker(last_write_task, global_context)
                    if VERBOSE:
                        console.print(f"[dim]  Reescritura: {retry_result}[/dim]")

                    # Volver a validar
                    revalidate_result = await run_worker(task, global_context)
                    if "OK" in revalidate_result or "Completado" in revalidate_result:
                        if VERBOSE:
                            console.print(f"[bold]  [Validación OK tras reintento {retry}][/bold]")
                        worker_result = revalidate_result
                        global_context += f"- Reintento exitoso de: {last_write_task}\n  Resultado: {retry_result}\n\n"
                        break
                    elif retry == MAX_VALIDATION_RETRIES:
                        if VERBOSE:
                            console.print(f"[bold]  [Advertencia][/bold] Chunk no corregido tras {MAX_VALIDATION_RETRIES} reintentos. Continuando...")
        else:
            if VERBOSE:
                console.print(f"[bold]  [Completado][/bold] {worker_result}")

        # Guardar el último paso de escritura para posibles reintentos
        if any(kw in task.lower() for kw in ["write_file", "append_file", "escribir", "append"]):
            last_write_task = task

        global_context += f"- Tarea: {task}\n  Resultado: {worker_result}\n\n"
        idx += 1

    if VERBOSE:
        console.print("\n[bold]> Sintetizando reporte final...[/bold]")
    synth_prompt = (
        "Eres el Synthesizer final. Lee la petición original del usuario y los resultados de las tareas ejecutadas.\n"
        "Redacta una respuesta final clara y concisa al usuario. No menciones 'agentes' ni procesos internos."
    )

    with console.status("[bold]Consolidando datos...[/bold]", spinner="line"):
        final_response = await query_ollama(synth_prompt, global_context, max_tokens=2048, temp=0.6)

    return final_response.strip()
