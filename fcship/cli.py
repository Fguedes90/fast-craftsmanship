"""CLI application entry point for fast-craftsmanship tool."""

import typer
import functools
from typing import Dict, Optional, Callable, Tuple, Any

from expression import Result
from rich.console import Console
from rich.table import Table

from . import __version__
from .commands import COMMANDS, COMMANDS_BY_CATEGORY, COMMAND_CATEGORIES
from .commands.github.cli import github_app

console = Console()

app = typer.Typer(
    help="""Fast-craftsmanship CLI tool for managing FastAPI project structure and code generation.
    
This tool helps you maintain a clean and consistent project structure following
domain-driven design principles and FastAPI best practices.""",
    name="craftsmanship",
    no_args_is_help=True,
)

# Create category-based subcommands
scaffold_app = typer.Typer(help=COMMAND_CATEGORIES["scaffold"])
vcs_app = typer.Typer(help=COMMAND_CATEGORIES["vcs"])
quality_app = typer.Typer(help=COMMAND_CATEGORIES["quality"])
db_app = typer.Typer(help=COMMAND_CATEGORIES["db"])
docs_app = typer.Typer(help=COMMAND_CATEGORIES["docs"])
scraper_app = typer.Typer(help=COMMAND_CATEGORIES["scraper"])

# Map category names to their respective app instances
CATEGORY_APPS: Dict[str, typer.Typer] = {
    "scaffold": scaffold_app,
    "vcs": vcs_app,
    "quality": quality_app,
    "db": db_app,
    "docs": docs_app,
    "scraper": scraper_app
}


def version_callback(value: bool) -> None:
    """Print version information and exit."""
    if value:
        console.print(f"[bold]Fast-craftsmanship[/bold] version: [cyan]{__version__}[/cyan]")
        raise typer.Exit()


def show_categories_callback(value: bool) -> None:
    """Show command categories and exit."""
    if value:
        table = Table(title="Fast-craftsmanship Command Categories")
        table.add_column("Category", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Commands", style="yellow")
        
        for category, description in COMMAND_CATEGORIES.items():
            commands = ", ".join(COMMANDS_BY_CATEGORY.get(category, {}).keys())
            table.add_row(category, description, commands or "None")
        
        console.print(table)
        raise typer.Exit()


def tui_callback(value: bool) -> None:
    """Launch the interactive Terminal UI."""
    if value:
        from .tui.menu import run_tui
        run_tui()
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
    categories: bool = typer.Option(
        None,
        "--categories",
        "-c",
        help="Show command categories and exit.",
        callback=show_categories_callback,
        is_eager=True,
    ),
    tui: bool = typer.Option(
        None,
        "--tui",
        "-t",
        help="Launch interactive Terminal UI menu.",
        callback=tui_callback,
        is_eager=True,
    ),
) -> None:
    """Fast-craftsmanship CLI tool for FastAPI projects."""
    pass


def handle_result(result: Result) -> None:
    """Handle Result type from commands"""
    if hasattr(result, "ok") and result.ok is not None:
        if isinstance(result.ok, str):
            console.print(f"[green]{result.ok}[/green]")
        else:
            console.print("[green]Command completed successfully[/green]")
    elif hasattr(result, "error") and result.error is not None:
        console.print(f"[red]Error: {result.error}[/red]")
        raise typer.Exit(1)
    else:
        console.print("[yellow]Warning: Command returned unexpected result type[/yellow]")


def wrap_command(cmd: Callable) -> Callable:
    """Wrap command to handle Result type while preserving signature"""
    @functools.wraps(cmd)  # This preserves the function signature
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            result = cmd(*args, **kwargs)
            if isinstance(result, Result):
                handle_result(result)
            return result
        except Exception as e:
            console.print(f"[red]Error: {e!s}[/red]")
            raise typer.Exit(1)

    return wrapper


# Register commands in both flat structure (for backward compatibility)
# and in category-based structure
for cmd_name, (cmd_func, help_text) in COMMANDS.items():
    wrapped = wrap_command(cmd_func)
    wrapped.__name__ = cmd_func.__name__
    wrapped.__doc__ = cmd_func.__doc__
    app.command(name=cmd_name, help=help_text)(wrapped)

# Register category-based commands
for category, commands in COMMANDS_BY_CATEGORY.items():
    if category_app := CATEGORY_APPS.get(category):
        for cmd_name, (cmd_func, help_text) in commands.items():
            wrapped = wrap_command(cmd_func)
            wrapped.__name__ = cmd_func.__name__
            wrapped.__doc__ = cmd_func.__doc__
            category_app.command(name=cmd_name, help=help_text)(wrapped)

# Add category typers to main app
for category, category_app in CATEGORY_APPS.items():
    app.add_typer(category_app, name=category)

# Add the GitHub commands
app.add_typer(github_app, name="github")


@app.command("menu")
def menu_command() -> None:
    """Launch the interactive Terminal UI menu."""
    from .tui.menu import run_tui
    run_tui()


def main() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
