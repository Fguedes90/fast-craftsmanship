"""API command implementation."""
import typer
from pathlib import Path
from fcship.templates.api_templates import get_api_templates
from fcship.utils import (
    handle_command_errors,
    validate_operation,
    success_message,
    file_creation_status,
    ensure_directory
)

@handle_command_errors
def create_api(name: str) -> None:
    """Create new API endpoint files."""
    files = get_api_templates(name)
    with file_creation_status("Creating API endpoint files...") as status:
        for file_path, content in files.items():
            path = Path(file_path)
            ensure_directory(path)
            path.write_text(content)
            status.add_file(str(path))
    success_message(f"Created API endpoint {name}")

def api(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the API route")
) -> None:
    """Create new API endpoint files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_api(name)