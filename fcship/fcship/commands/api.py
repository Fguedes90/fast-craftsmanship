"""API command implementation."""
import typer
from ..templates.api_templates import get_api_templates
from ..utils import handle_command_errors, create_files, validate_operation, success_message

@handle_command_errors
def create_api(name: str) -> None:
    """Create new API endpoint files."""
    files = get_api_templates(name)
    create_files(files)
    success_message(f"Created API endpoint {name}")

def api(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the API route")
) -> None:
    """Create new API endpoint files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_api(name)