import asyncio
import os
import sys
import json
import datetime
import httpx
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.rule import Rule
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
from rich import box
from agent import run_agent
from state_manager import mqtt_listener_loop

console = Console()

SESSIONS_DIR = Path("sessions")
SESSIONS_DIR.mkdir(exist_ok=True)

LOGO = """\
 ██████╗  █████╗ ███████╗██████╗ ██╗ █████╗
 ██╔══██╗██╔══██╗██╔════╝██╔══██╗██║██╔══██╗
 ██████╔╝███████║███████╗██████╔╝██║███████║
 ██╔══██╗██╔══██║╚════██║██╔═══╝ ██║██╔══██║
 ██║  ██║██║  ██║███████║██║     ██║██║  ██║
 ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝"""

COMMANDS = {
    "/nuevo":    "Iniciar nueva conversación",
    "/modelos":  "Ver modelos disponibles en Ollama",
    "/historial":"Ver sesiones guardadas",
    "/salir":    "Salir de RaspIA",
}


# ── Ollama ─────────────────────────────────────────────────────────────────

async def fetch_models() -> list[str]:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://localhost:11434/api/tags")
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []


async def set_model(model: str):
    """Escribe el modelo elegido en llm_client.py de forma dinámica."""
    lc = Path("llm_client.py").read_text()
    import re
    lc = re.sub(r'"model":\s*"[^"]+"', f'"model": "{model}"', lc)
    Path("llm_client.py").write_text(lc)


# ── Sesiones ───────────────────────────────────────────────────────────────

def new_session_path() -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return SESSIONS_DIR / f"session_{ts}.json"


def save_message(path: Path, role: str, content: str):
    data = json.loads(path.read_text()) if path.exists() else {"messages": []}
    data["messages"].append({
        "role": role,
        "ts": datetime.datetime.now().isoformat(),
        "content": content
    })
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def list_sessions() -> list[Path]:
    return sorted(SESSIONS_DIR.glob("*.json"), reverse=True)[:10]


# ── UI helpers ─────────────────────────────────────────────────────────────

def clear():
    os.system("clear" if sys.platform != "win32" else "cls")


def print_logo(model: str):
    clear()
    w = console.width
    for line in LOGO.split("\n"):
        pad = max(0, (w - len(line)) // 2)
        console.print(" " * pad + line, style="bold white")
    console.print()
    mid = f"  Edge AI · Raspberry Pi 5 · {model}  "
    pad = max(0, (w - len(mid)) // 2)
    console.print(" " * pad + mid, style="dim")
    console.print()
    console.print(Rule(style="white"))
    console.print(
        "  [bold]/nuevo[/bold]  [bold]/modelos[/bold]  "
        "[bold]/historial[/bold]  [bold]/salir[/bold]",
        style="dim"
    )
    console.print(Rule(style="white"))
    console.print()


def bubble_user(msg: str):
    w = console.width
    text = Text()
    text.append("  You  ", style="reverse bold white")
    text.append(f"  {msg}", style="white")
    console.print()
    console.print(text)


def bubble_agent(msg: str):
    console.print()
    console.print(Rule(" RaspIA ", style="white", align="left"))
    console.print(Markdown(msg.strip()))
    console.print(Rule(style="dim"))


def show_commands():
    console.print()
    console.print(Rule(" Comandos ", style="white"))
    for cmd, desc in COMMANDS.items():
        console.print(f"  [bold]{cmd}[/bold]  [dim]{desc}[/dim]")
    console.print()


async def show_models(current: str) -> str:
    console.print()
    with console.status("[bold]Consultando Ollama...[/bold]", spinner="line"):
        models = await fetch_models()

    if not models:
        console.print("  [dim]No se encontraron modelos. ¿Está Ollama corriendo?[/dim]")
        return current

    console.print(Rule(" Modelos disponibles ", style="white"))
    for i, m in enumerate(models, 1):
        marker = "[bold]▶[/bold] " if m == current else "  "
        console.print(f"  {marker}[{i}] {m}")
    console.print()

    raw = await asyncio.to_thread(input, "  Selecciona número (Enter para mantener actual): ")
    try:
        chosen = models[int(raw.strip()) - 1]
        await set_model(chosen)
        console.print(f"  [bold]Modelo cambiado a:[/bold] {chosen}")
        return chosen
    except (ValueError, IndexError):
        return current


def show_sessions():
    sessions = list_sessions()
    console.print()
    if not sessions:
        console.print("  [dim]No hay sesiones guardadas aún.[/dim]")
        return
    console.print(Rule(" Últimas sesiones ", style="white"))
    for p in sessions:
        data = json.loads(p.read_text())
        n = len(data.get("messages", []))
        ts = p.stem.replace("session_", "").replace("_", " ")
        console.print(f"  [dim]{ts}[/dim]  [{n} mensajes]  {p.name}")
    console.print()


# ── Loop principal ─────────────────────────────────────────────────────────

async def chat_loop(model: str):
    print_logo(model)
    session_path = new_session_path()
    historial = ""
    msg_count = 0

    console.print(
        "  [dim]Nueva sesión iniciada → guardando en[/dim] "
        f"[bold]{session_path.name}[/bold]\n"
    )

    while True:
        try:
            raw = await asyncio.to_thread(input, "  ❯ ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n  [dim]Sesión interrumpida.[/dim]")
            break

        user_input = raw.strip()
        if not user_input:
            continue

        # ── Comandos ──────────────────────────────────────────────────
        if user_input == "/salir":
            console.print("\n  [dim]Hasta luego.[/dim]")
            break

        if user_input == "/nuevo":
            session_path = new_session_path()
            historial = ""
            msg_count = 0
            print_logo(model)
            console.print(f"  [dim]Nueva sesión → {session_path.name}[/dim]\n")
            continue

        if user_input == "/modelos":
            model = await show_models(model)
            continue

        if user_input == "/historial":
            show_sessions()
            continue

        if user_input == "/ayuda":
            show_commands()
            continue

        # ── Mensaje normal ────────────────────────────────────────────
        bubble_user(user_input)
        save_message(session_path, "user", user_input)
        msg_count += 1

        # Spinner mientras el agente trabaja
        with Live(Spinner("line", text="  [dim]RaspIA pensando...[/dim]"),
                  refresh_per_second=12, console=console):
            response = await run_agent(user_input, historial)

        historial += f"\nUsuario: {user_input}\nAsistente: {response.strip()}"
        save_message(session_path, "assistant", response.strip())

        bubble_agent(response)
        console.print(
            f"  [dim]  #{msg_count} · {session_path.name}[/dim]\n"
        )


# ── Selector de modelo inicial ─────────────────────────────────────────────

async def select_model_startup() -> str:
    with console.status("[bold]Detectando modelos en Ollama...[/bold]", spinner="line"):
        models = await fetch_models()

    clear()
    w = console.width
    for line in LOGO.split("\n"):
        pad = max(0, (w - len(line)) // 2)
        console.print(" " * pad + line, style="bold white")
    console.print()
    console.print(Rule(style="white"))

    if not models:
        console.print("  [dim]Ollama no responde. Usando modelo por defecto.[/dim]")
        return "qwen2.5-coder:3b"

    console.print("  [bold]Selecciona modelo de inicio:[/bold]\n")
    for i, m in enumerate(models, 1):
        console.print(f"    [{i}]  {m}")
    console.print()

    raw = await asyncio.to_thread(input, "  Número: ")
    try:
        chosen = models[int(raw.strip()) - 1]
        await set_model(chosen)
        return chosen
    except (ValueError, IndexError):
        return models[0]


# ── Entry point ────────────────────────────────────────────────────────────

async def main():
    model = await select_model_startup()
    listener_task = asyncio.create_task(mqtt_listener_loop())
    try:
        await chat_loop(model)
    finally:
        listener_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
