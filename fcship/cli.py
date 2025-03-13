import typer
from rich.console import Console
from rich.panel import Panel
from .command_list import COMMANDS
import dotenv
from typing import Any

dotenv.load_dotenv()

app = typer.Typer(
    help="AI Dev Toolkit - A developer's best friend",
    add_completion=False,
)
console = Console()

@app.command()
def start():
    console.print(Panel.fit(
        "[bold green]AI Dev Toolkit[/]\n[blue]Welcome to your development assistant![/]",
        border_style="green"
    ))
    
    for cmd in COMMANDS.values():
        cmd.display_info()

    help_text = "[bold blue]Help:[/]\n[blue]Available commands:[/]\n"
    for cmd in COMMANDS.values():
        help_text += f"[bold green]{cmd.name}[/] - {cmd.help}\n"
    
    console.print(Panel.fit(help_text, border_style="blue"))

def register_command(name: str, command: Any) -> None:
    @app.command(name=name)
    def dynamic_command(param: str | None = typer.Argument(None)):
        command.execute(param)

# Dynamically register all commands
for name, command in COMMANDS.items():
    register_command(name, command)

@app.command()
def version():
    console.print("[bold cyan]AI Dev Toolkit v0.1.0[/] 🚀")

if __name__ == "__main__":
    app()