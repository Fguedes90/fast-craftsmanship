"""Domain command implementation."""
import typer
from pathlib import Path
from ..templates.domain_templates import get_domain_templates
from ..utils import handle_command_errors, create_files, validate_operation, success_message

@handle_command_errors
def create_domain(name: str) -> None:
    """Create a new domain with all required files."""
    files = get_domain_templates(name)
    create_files(files, base_path=f"domain/{name}")
    success_message(f"Created domain {name}")

def domain(
    operation: str = typer.Argument(..., help="Operation to perform [create]"), 
    name: str = typer.Argument(..., help="Name of the domain")
) -> None:
    """Create a new domain with all required files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_domain(name)