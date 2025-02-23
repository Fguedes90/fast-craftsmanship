"""Repository command implementation."""
import typer
from pathlib import Path
from fcship.templates.repo_templates import get_repo_templates
from fcship.utils import (
    handle_command_errors,
    validate_operation,
    success_message,
    file_creation_status,
    ensure_directory
)

@handle_command_errors
def create_repo(name: str) -> None:
    """Create repository implementation files."""
    files = get_repo_templates(name)
    with file_creation_status("Creating repository files...") as status:
        for file_path, content in files.items():
            path = Path(file_path)
            ensure_directory(path)
            path.write_text(content)
            status.add_file(str(path))
    success_message(f"Created repository {name}")

def repo(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the repository")
) -> None:
    """Create repository implementation files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_repo(name)