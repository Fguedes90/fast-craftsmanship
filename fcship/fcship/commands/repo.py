"""Repository command implementation."""
import typer
from ..templates.repo_templates import get_repo_templates
from ..utils import handle_command_errors, create_files, validate_operation, success_message

@handle_command_errors
def create_repo(name: str) -> None:
    """Create repository implementation files."""
    files = get_repo_templates(name)
    create_files(files)
    success_message(f"Created repository {name}")

def repo(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the repository")
) -> None:
    """Create repository implementation files."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_repo(name)