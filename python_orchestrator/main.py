import asyncio
import aiomqtt
import json
import re
from llm_client import query_ollama
from tool_executor import execute_tool
from vision import get_camera_labels
from skills_manager import load_skills
from rich.console import Console
from rich.panel import Panel

console = Console()

async def react_agent_loop(client: aiomqtt.Client, payload: str):
    console.print(f"\n[cyan]📥 Telemetría recibida:[/cyan] {payload}")
    
    # 1. Obtener etiquetas de picamera2
    vision_labels = get_camera_labels()
    
    # 2. Cargar habilidades dinámicas
    skills_context = load_skills()
    
    # 3. Construcción de prompt con contexto acotado
    system_prompt = (
        "You are an offline edge AI assistant. Think clearly but DO NOT output reasoning. "
        "Analyze the context. If action is required, output strictly a valid JSON format: "
        "{\"tool\": \"name\", \"args\": [\"arg1\"]}. "
        f"Available skills:\n{skills_context}"
    )
    context = f"Telemetry: {payload} | Vision: {vision_labels}"
    
    # 4. Inferencia LLM
    with console.status("[bold yellow]🧠 Orquestador Cognitivo analizando...", spinner="bouncingBar"):
        raw_response = await query_ollama(system_prompt, context)
    
    # 5. Saneamiento robusto de JSON
    match = re.search(r'\{.*\}', raw_response, re.DOTALL)
    if match:
        try:
            tool_call = json.loads(match.group(0))
            console.print(Panel(f"[bold green]Herramienta Seleccionada:[/bold green] {tool_call.get('tool')}\n[bold green]Argumentos:[/bold green] {tool_call.get('args')}", title="🤖 Decisión de IA", border_style="green"))
            await execute_tool(tool_call)
        except json.JSONDecodeError:
            console.print("[bold red]Error:[/bold red] JSON mal formado generado por el modelo.")
    else:
        console.print("[dim]✅ Sistema estable. Sin acciones requeridas.[/dim]")

async def start_orchestrator():
    async with aiomqtt.Client("127.0.0.1") as client:
        await client.subscribe("iot/telemetry/sensors")
        console.print(Panel.fit("[bold blue]🚀 Orquestador Edge IoT Iniciado[/bold blue]\n[dim]Escuchando telemetría MQTT en 127.0.0.1:1883...[/dim]", border_style="blue"))
        async for message in client.messages:
            payload = message.payload.decode()
            # Despachar tarea asíncrona
            asyncio.create_task(react_agent_loop(client, payload))

if __name__ == "__main__":
    asyncio.run(start_orchestrator())
