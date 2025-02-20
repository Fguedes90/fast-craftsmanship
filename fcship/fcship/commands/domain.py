"""Domain command implementation."""
import typer
from pathlib import Path
from ..templates.domain_templates import get_domain_templates
from ..utils import (
    handle_command_errors,
    validate_operation,
    success_message,
    file_creation_status,
    ensure_directory
)

@handle_command_errors
def create_domain(name: str) -> None:
    """Create a new domain with all required files."""
    files = get_domain_templates(name)
    with file_creation_status("Creating domain files...") as status:
        for file_path, content in files.items():
            path = Path(f"domain/{name}") / file_path
            ensure_directory(path)
            path.write_text(content)
            status.add_file(str(path))
    success_message(f"Created domain {name}")

def domain(
    operation: str = typer.Argument(..., help="Operation to perform [create]"), 
    name: str = typer.Argument(..., help="Name of the domain")
) -> None:
    """Create a new domain with all required files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_domain(name)