import asyncio
import os
import sys
from rich.console import Console

console = Console()

async def execute_tool(tool_call: dict) -> str:
    tool_name = tool_call.get("tool")
    args = tool_call.get("args", [])
    
    script_path = f"../scripts/tools/{tool_name}.py"
    
    if not os.path.exists(script_path):
        err = f"Tool {tool_name} no encontrada en {script_path}."
        console.print(f"[bold]  [ERROR][/bold] {err}")
        return err

    native_tools = ["system_bash", "write_file", "read_file"]
    # Bypass de bwrap si estamos en Mac o si explícitamente es la herramienta de control nativo
    if sys.platform == "darwin" or tool_name in native_tools:
        console.print(f"[dim]  (Modo Nativo {sys.platform}) -> {tool_name}[/dim]")
        cmd = ["python3", script_path] + [str(a) for a in args]
    else:
        # Configuración para Linux / Raspberry Pi
        console.print(f"[dim]  (Modo Sandbox bwrap) -> {tool_name}[/dim]")
        cmd = [
            "bwrap",
            "--ro-bind", "/", "/",
            "--dev", "/dev",
            "--proc", "/proc",
            "--tmpfs", "/tmp",
            "--unshare-all",
            "--share-net", # Permitir red si es necesario (ej. para Ollama si fuera externo, pero aquí es local)
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
    
    if err_str and not out_str:
        console.print(f"[bold]  [ERROR][/bold] {err_str}")
        return err_str
    else:
        # A veces stderr tiene warnings pero la ejecución fue exitosa
        return out_str
