"""CLI application entry point for fast-craftsmanship tool."""

import typer

from expression import Result
from rich.console import Console

from . import __version__
from .commands import COMMANDS
from .commands.github.cli import github_app

# from .commands.api import api
# from .commands.domain import domain
# from .commands.service import service
# from .commands.repo import repo
# from .commands.project import project
# from .commands.test import test
# from .commands.verify import verify
# from .commands.docs_downloader import docs

console = Console()

app = typer.Typer(
    help="""Fast-craftsmanship CLI tool for managing FastAPI project structure and code generation.
    
This tool helps you maintain a clean and consistent project structure following
domain-driven design principles and FastAPI best practices.""",
    name="craftsmanship",
    no_args_is_help=True,
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


def handle_result(result: Result) -> None:
    """Handle Result type from commands"""
    if hasattr(result, "ok"):
        if isinstance(result.ok, str):
            console.print(f"[green]{result.ok}[/green]")
    elif hasattr(result, "error"):
        console.print(f"[red]Error: {result.error}[/red]")
        raise typer.Exit(1)
    else:
        console.print("[yellow]Warning: Command returned unexpected result type[/yellow]")


def wrap_command(cmd):
    """Wrap command to handle Result type"""

    def wrapper(*args, **kwargs):
        try:
            # Extract actual arguments from kwargs if they exist
            if "args" in kwargs and "kwargs" in kwargs:
                args = (kwargs["args"], kwargs["kwargs"])
                kwargs = {}
            result = cmd(*args, **kwargs)
            if isinstance(result, Result):
                handle_result(result)
            return result
        except Exception as e:
            console.print(f"[red]Error: {e!s}[/red]")
            raise typer.Exit(1)

    return wrapper


# Register all commands
for cmd_name, (cmd_func, help_text) in COMMANDS.items():
    wrapped = wrap_command(cmd_func)
    wrapped.__name__ = cmd_func.__name__
    wrapped.__doc__ = cmd_func.__doc__
    app.command(name=cmd_name, help=help_text)(wrapped)

# Add the GitHub commands
app.add_typer(github_app)


def main() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
