"""Service command implementation."""
import typer
from pathlib import Path
from ..templates.service_templates import get_service_templates
from ..utils import (
    handle_command_errors,
    validate_operation,
    success_message,
    file_creation_status,
    ensure_directory
)

@handle_command_errors
def create_service(name: str) -> None:
    """Create a new service with required files."""
    files = get_service_templates(name)
    with file_creation_status("Creating service files...") as status:
        for file_path, content in files.items():
            path = Path(f"service/{name}") / file_path
            ensure_directory(path)
            path.write_text(content)
            status.add_file(str(path))
    success_message(f"Created service {name}")

def service(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the service")
) -> None:
    """Create a new service with required files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_service(name)