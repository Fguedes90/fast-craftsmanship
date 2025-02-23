"""Project initialization command."""
import typer
from pathlib import Path
from rich.panel import Panel
from fcship.utils import (
    handle_command_errors, 
    file_creation_status, 
    validate_operation, 
    success_message,
    console
)
from fcship.templates.project_templates import get_project_templates

@handle_command_errors
def init_project(name: str) -> None:
    """Initialize new project structure."""
    folders = [
        "domain",
        "service",
        "api/v1",
        "api/schemas",
        "infrastructure/repositories",
        "tests/unit",
        "tests/integration",
        "tests/api"
    ]
    
    root = Path(name)
    # Create project structure
    with file_creation_status("Creating project structure...") as status:
        # Create directories
        for folder in folders:
            (root / folder).mkdir(parents=True, exist_ok=True)
            status.add_file(f"{name}/{folder}", "Created directory")
        
        # Create project files
        files = get_project_templates(name)
        for file_path, content in files.items():
            path = root / file_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            status.add_file(f"{name}/{file_path}")
    
    success_message(f"Initialized project {name}")
    
    # Show next steps in a nice panel
    next_steps = """
1. [cyan]cd[/cyan] """ + name + """
2. [cyan]python -m venv .venv && source .venv/bin/activate[/cyan]
3. [cyan]pip install -e ".[dev]"[/cyan]
4. Start creating your domains with: [green]craftsmanship domain create <name>[/green]
"""
    console.print(Panel(next_steps, title="[bold]Next Steps", border_style="green"))

def project(
    operation: str = typer.Argument(..., help="Operation to perform [init]"),
    name: str = typer.Argument(..., help="Name of the project")
) -> None:
    """Initialize new project with basic structure."""
    validate_operation(operation, ["init"], name, requires_name=["init"])
    init_project(name)