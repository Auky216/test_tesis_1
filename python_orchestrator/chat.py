import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from agent import run_agent
from state_manager import mqtt_listener_loop

console = Console()

async def interactive_loop():
    console.print(Panel.fit("[bold]=== OPENCLAW EDGE AI ===[/bold]\n[dim]Escribe 'salir' para detener la ejecución.[/dim]", border_style="white"))
    
    historial = ""
    
    while True:
        try:
            user_input = await asyncio.to_thread(Prompt.ask, "\n[bold]User[/bold]")
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                console.print("[dim]Terminando sesión...[/dim]")
                break
                
            if not user_input.strip():
                continue
                
            final_response = await run_agent(user_input, historial)
            
            historial += f"\nUsuario: {user_input}\nAsistente: {final_response.strip()}"
            
            console.print(Panel(Markdown(final_response.strip()), title="[bold]Agent Response[/bold]", border_style="white"))
            
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupción de usuario. Saliendo...[/dim]")
            break
        except Exception as e:
            console.print(f"[reverse] ERROR CRÍTICO [/reverse] {e}")
            break

async def main():
    listener_task = asyncio.create_task(mqtt_listener_loop())
    await interactive_loop()
    listener_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
