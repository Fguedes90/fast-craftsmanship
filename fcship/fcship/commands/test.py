"""Test command implementation."""
import typer
from ..templates.test_templates import get_test_template
from ..utils import handle_command_errors, create_files, validate_operation, success_message, error_message

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
    files = {f"tests/{test_type}/{name}/test_{name}.py": content}
    create_files(files)
    success_message(f"Created {test_type} test {name}")

def test(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    test_type: str = typer.Argument(..., help="Type of test [unit/integration]"),
    name: str = typer.Argument(..., help="Name of the test")
) -> None:
    """Create test files based on type."""
    validate_operation(operation, ["create"], name, requires_name=["create"])
    create_test(test_type, name)