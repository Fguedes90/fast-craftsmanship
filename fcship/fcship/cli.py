"""CLI application entry point for fast-craftsmanship tool."""
import typer
from rich.console import Console
from . import __version__
from .commands import COMMANDS
from .commands.api import api
from .commands.domain import domain
from .commands.service import service
from .commands.repo import repo
from .commands.project import project
from .commands.test import test
from .commands.verify import verify
from .commands.docs_downloader import docs

console = Console()

app = typer.Typer(
    help="""Fast-craftsmanship CLI tool for managing FastAPI project structure and code generation.
    
This tool helps you maintain a clean and consistent project structure following
domain-driven design principles and FastAPI best practices.""",
    name="craftsmanship",
    no_args_is_help=True
)

def version_callback(value: bool) -> None:
    """Print version information and exit."""
    if value:
        console.print(f"[bold]Fast-craftsmanship[/bold] version: [cyan]{__version__}[/cyan]")
        raise typer.Exit()

@app.callback()
def callback(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version information and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """Fast-craftsmanship CLI tool for FastAPI projects."""
    pass

# Register all commands
for cmd_name, (cmd_func, help_text) in COMMANDS.items():
    app.command(help=help_text)(cmd_func)

app.command()(api)
app.command()(domain)
app.command()(service)
app.command()(repo)
app.command()(project)
app.command()(test)
app.command()(verify)
app.command()(docs)

def main() -> None:
    """CLI entry point."""
    app()

if __name__ == "__main__":
    main()
