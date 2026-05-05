import asyncio
from llm_client import query_ollama
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

async def main():
    console.print(Panel.fit("[bold cyan]=== Chat Interactivo Edge AI ===[/bold cyan]\n[dim]Escribe 'salir' para terminar.[/dim]", border_style="cyan"))
    
    # Un prompt genérico
    system_prompt = "Eres un experto en Edge Computing, IoT y Rust. Responde en español de forma útil y clara."
    
    # Aquí guardaremos la memoria de la conversación
    historial = ""
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]Tú[/bold green]")
            if user_input.lower() in ['salir', 'exit', 'quit']:
                console.print("[dim]Saliendo...[/dim]")
                break
                
            if not user_input.strip():
                continue
                
            with console.status("[bold yellow]IA pensando...", spinner="dots"):
                # Unimos el historial pasado con la pregunta nueva
                contexto_completo = f"{historial}\nUsuario: {user_input}"
                
                response = await query_ollama(system_prompt, contexto_completo, max_tokens=2048, temp=0.7)
            
            # Actualizamos el historial para la próxima vuelta
            historial += f"\nUsuario: {user_input}\nAsistente: {response.strip()}"
            
            console.print(Panel(Markdown(response.strip()), title="[bold magenta]Modelo Local[/bold magenta]", border_style="magenta"))
            
        except KeyboardInterrupt:
            console.print("\n[dim]Saliendo...[/dim]")
            break

if __name__ == "__main__":
    asyncio.run(main())
