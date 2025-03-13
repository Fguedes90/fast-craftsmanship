"""CLI entry point for Fast Craftsmanship."""
import typer
from rich.console import Console
from rich.panel import Panel
from .command_list import COMMANDS
import dotenv
from typing import Optional

dotenv.load_dotenv()

app = typer.Typer(
    help="Fast Craftsmanship - Developer's toolkit for fast and clean development",
    add_completion=False,
)

console = Console()

@app.command()
def start():
    """Show welcome message and available commands."""
    console.print(Panel.fit(
        "[bold green]Fast Craftsmanship[/]\n[blue]Welcome to your development toolkit![/]",
        border_style="green"
    ))
    
    for cmd in COMMANDS.values():
        cmd.display_info()

def register_command(name: str, command: 'Command') -> None:
    """Register a command with the CLI."""
    @app.command(name=name, help=command.help)
    def dynamic_command(
        operation: Optional[str] = typer.Argument(None, help="Operation to perform"),
        name: Optional[str] = typer.Argument(None, help="Name parameter (if required)"),
    ):
        command.execute(operation, name)

# Dynamically register all commands
for name, command in COMMANDS.items():
    register_command(name, command)

@app.command()
def version():
    """Show version information."""
    console.print("[bold cyan]Fast Craftsmanship v0.1.0[/] 🚀")

def main():
    """Main entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()