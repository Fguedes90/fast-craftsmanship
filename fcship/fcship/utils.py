"""Shared utilities for CLI commands."""
from typing import Callable, TypeVar, Any, Dict, List, Optional
from pathlib import Path
import typer
from functools import wraps
from rich.console import Console
from rich.panel import Panel

T = TypeVar('T')
console = Console()

def ensure_directory(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.parent.mkdir(parents=True, exist_ok=True)

def create_files(files: Dict[str, str], base_path: str = "") -> None:
    """Create multiple files with their contents.
    
    Args:
        files: Dictionary mapping file paths to their contents
        base_path: Optional base path to prepend to all file paths
    """
    with console.status("[bold green]Creating files..."):
        for file_path, content in files.items():
            path = Path(base_path) / file_path if base_path else Path(file_path)
            ensure_directory(path)
            path.write_text(content)
            console.print(f"Created: [cyan]{path}[/cyan]")

def validate_operation(
    operation: str,
    valid_operations: List[str],
    name: Optional[str] = None,
    requires_name: Optional[List[str]] = None
) -> None:
    """Validate command operation and arguments.
    
    Args:
        operation: The operation to validate
        valid_operations: List of valid operation names
        name: Optional name argument to validate
        requires_name: List of operations that require a name argument
    """
    if operation not in valid_operations:
        operations_str = ", ".join(f"[cyan]{op}[/cyan]" for op in valid_operations)
        console.print(Panel(
            f"[red]Unknown operation:[/red] [bold]{operation}[/bold]\n\n"
            f"Available operations: {operations_str}",
            title="Error",
            border_style="red"
        ))
        raise typer.Exit(1)
    
    if requires_name and operation in requires_name and not name:
        console.print(Panel(
            f"[red]Operation '[cyan]{operation}[/cyan]' requires a name argument[/red]",
            title="Error",
            border_style="red"
        ))
        raise typer.Exit(1)

def handle_command_errors(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to handle common command errors consistently."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
        except FileExistsError as e:
            console.print(Panel(
                f"[red]File already exists:[/red] [cyan]{e.filename}[/cyan]",
                title="Error",
                border_style="red"
            ))
            raise typer.Exit(1)
        except PermissionError as e:
            console.print(Panel(
                f"[red]Permission denied:[/red] [cyan]{e.filename}[/cyan]\n"
                "Try running the command with appropriate permissions",
                title="Error",
                border_style="red"
            ))
            raise typer.Exit(1)
        except Exception as e:
            console.print(Panel(
                f"[red]An unexpected error occurred:[/red]\n{str(e)}",
                title="Error",
                border_style="red"
            ))
            raise typer.Exit(1)
    return wrapper

def success_message(message: str) -> None:
    """Print a success message with consistent styling."""
    console.print(f"[bold green]✨[/bold green] {message}")

def error_message(message: str, details: Optional[str] = None) -> None:
    """Print an error message with consistent styling."""
    panel_content = f"[red]{message}[/red]"
    if details:
        panel_content += f"\n\n{details}"
    console.print(Panel(panel_content, title="Error", border_style="red"))