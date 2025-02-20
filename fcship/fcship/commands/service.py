"""Service command implementation."""
import typer
from ..templates.service_templates import get_service_templates
from ..utils import handle_command_errors, create_files, validate_operation, success_message

@handle_command_errors
def create_service(name: str) -> None:
    """Create a new service with required files."""
    files = get_service_templates(name)
    create_files(files, base_path=f"service/{name}")
    success_message(f"Created service {name}")

def service(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the service")
) -> None:
    """Create a new service with required files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_service(name)