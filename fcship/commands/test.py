"""Test command implementation."""
import typer
from pathlib import Path
from fcship.templates.test_templates import get_test_template
from fcship.utils import (
    handle_command_errors,
    validate_operation,
    success_message,
    error_message,
    file_creation_status,
    ensure_directory
)

@handle_command_errors
def create_test(test_type: str, name: str) -> None:
    """Create test files."""
    if test_type not in ["unit", "integration"]:
        error_message(
            f"Unknown test type: {test_type}",
            "Available test types: unit, integration"
        )
        raise typer.Exit(1)
    
    content = get_test_template(test_type, name)
    with file_creation_status(f"Creating {test_type} test files...") as status:
        file_path = f"tests/{test_type}/{name}/test_{name}.py"
        path = Path(file_path)
        ensure_directory(path)
        path.write_text(content)
        status.add_file(str(path))
    success_message(f"Created {test_type} test {name}")

def test(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    test_type: str = typer.Argument(..., help="Type of test [unit/integration]"),
    name: str = typer.Argument(..., help="Name of the test")
) -> None:
    """Create test files based on type."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_test(test_type, name)