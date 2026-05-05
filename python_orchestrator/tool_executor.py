import asyncio
import os
import sys
from rich.console import Console

console = Console()

async def execute_tool(tool_call: dict):
    tool_name = tool_call.get("tool")
    args = tool_call.get("args", [])
    
    script_path = f"../scripts/tools/{tool_name}.py"
    
    if not os.path.exists(script_path):
        console.print(f"[bold red]❌ Tool {tool_name} no encontrada en {script_path}.[/bold red]")
        return

    # Si estamos en macOS (darwin), bwrap no existe. Hacemos bypass para test local.
    if sys.platform == "darwin":
        console.print(f"[yellow][WARNING] Ejecutando '{tool_name}' de forma nativa. Sandboxing deshabilitado en macOS.[/yellow]")
        cmd = ["python3", script_path] + [str(a) for a in args]
    else:
        # Construcción de la jaula en Linux (Raspberry Pi)
        cmd = [
            "bwrap",
            "--ro-bind", "/", "/",
            "--dev", "/dev",
            "--unshare-net",
            "--tmpfs", "/tmp",
            "python3", script_path
        ] + [str(a) for a in args]
    
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    out_str = stdout.decode().strip()
    err_str = stderr.decode().strip()
    
    if err_str:
        console.print(f"[bold red]❌ Error en Tool {tool_name}:[/bold red] {err_str}")
    else:
        console.print(f"[bold cyan]⚡ Resultado de Acción:[/bold cyan] {out_str}")
