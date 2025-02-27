"""Service command implementation."""

from pathlib import Path

import typer

from fcship.templates.service_templates import get_service_templates
from fcship.utils import (
    ensure_directory,
    file_creation_status,
    handle_command_errors,
    success_message,
    validate_operation,
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
    name: str = typer.Argument(..., help="Name of the service"),
) -> None:
    """Create a new service with required files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_service(name)
