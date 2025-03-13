"""Test command implementation using Railway Oriented Programming."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import typer
from expression import Error, Ok, effect, tagged_union, Result
from rich.console import Console

from fcship.templates.test_templates import get_test_template
from fcship.tui.display import DisplayContext, error_message, success_message
from fcship.utils.error_handling import handle_command_errors
from fcship.utils.file_utils import ensure_directory, write_file
from fcship.utils import console
from .base import Command


@tagged_union
class TestError:
    """Tagged union for test command errors."""

    tag: Literal["validation_error", "file_error"]
    validation_error: str | None = None
    file_error: tuple[str, str] | None = None

    @staticmethod
    def ValidationError(message: str) -> "TestError":
        """Creates a validation error."""
        return TestError(tag="validation_error", validation_error=message)

    @staticmethod
    def FileError(path: str, details: str) -> "TestError":
        """Creates a file operation error."""
        return TestError(tag="file_error", file_error=(path, details))


@dataclass(frozen=True)
class TestContext:
    """Immutable context for test creation."""

    test_type: str
    name: str
    content: str
    file_path: Path


@effect.result[str, TestError]()
def validate_test_type(test_type: str):
    """Validate the test type."""
    valid_types = ["unit", "integration"]

    if test_type not in valid_types:
        yield Error(
            TestError.ValidationError(
                f"Invalid test type '{test_type}'. Must be one of: {', '.join(valid_types)}"
            )
        )
        return

    yield Ok(test_type)


@effect.result[str, str]()
def validate_test_operation(operation: str):
    """Validate test operation"""
    valid_operations = ["run", "watch"]
    if operation in valid_operations:
        yield Ok(operation)
    else:
        yield Error(f"Invalid operation '{operation}'. Supported operations: {', '.join(valid_operations)}")


@effect.result[TestContext, TestError]()
def prepare_test_context(test_type: str, name: str):
    """Prepare test context with template and file path."""
    try:
        # Get the template content
        content = get_test_template(test_type, name)

        # Create file path
        file_path = Path(f"tests/{test_type}/{name}/test_{name}.py")

        # Create context
        yield Ok(TestContext(test_type=test_type, name=name, content=content, file_path=file_path))
    except Exception as e:
        yield Error(TestError.ValidationError(f"Failed to prepare test context: {e!s}"))


@effect.result[Path, TestError]()
def ensure_test_directory(ctx: TestContext):
    """Ensure the test directory exists."""
    try:
        directory = ctx.file_path.parent
        result = ensure_directory(directory)

        if result.is_error():
            yield Error(
                TestError.FileError(str(directory), f"Failed to create directory: {result.error}")
            )
            return

        yield Ok(directory)
    except Exception as e:
        yield Error(
            TestError.FileError(str(ctx.file_path.parent), f"Failed to create directory: {e!s}")
        )


@effect.result[Path, TestError]()
def write_test_file(ctx: TestContext, display_ctx: DisplayContext = None):
    """Write the test file to disk."""
    try:
        # Write file content
        result = write_file(ctx.file_path, ctx.content)

        if result.is_error():
            yield Error(
                TestError.FileError(str(ctx.file_path), f"Failed to write file: {result.error}")
            )
            return

        yield Ok(ctx.file_path)
    except Exception as e:
        yield Error(TestError.FileError(str(ctx.file_path), f"Failed to write file: {e!s}"))


@effect.result[str, TestError]()
def handle_test_error(error: TestError, ctx: DisplayContext = None):
    """Handle test errors with proper UI feedback."""
    display_ctx = ctx or DisplayContext(console=Console())

    match error:
        case TestError(tag="validation_error") if error.validation_error is not None:
            yield from error_message(display_ctx, "Validation Error", error.validation_error)
        case TestError(tag="file_error") if error.file_error is not None:
            path, details = error.file_error
            yield from error_message(display_ctx, f"File Error: {path}", details)
        case _:
            yield from error_message(display_ctx, "Unknown Error", "An unknown error occurred")

    yield Error(error)


@effect.result[str, str]()
def run_tests(watch: bool = False):
    """Run the tests."""
    try:
        console.print("[blue]Running tests...[/]")
        # Note: Implementation for running tests will go here
        # For now, just return a placeholder message
        msg = "Tests running in watch mode..." if watch else "Tests completed"
        yield Ok(msg)
    except Exception as e:
        yield Error(f"Failed to run tests: {e!s}")


@effect.result[str, str]()
def test(
    operation: str = typer.Argument("run", help="Operation to perform [run, watch]"),
) -> Result[str, str]:
    """Run project tests."""
    try:
        # Validate operation
        operation_result = yield from validate_test_operation(operation)
        if operation_result.is_error():
            yield Error(operation_result.error)
            return

        # Execute operation
        if operation == "watch":
            result = yield from run_tests(watch=True)
        else:
            result = yield from run_tests(watch=False)

        if result.is_error():
            yield Error(result.error)
            return
        
        yield Ok(result.ok)
    except Exception as e:
        yield Error(f"Unexpected error: {e!s}")


class TestCommand(Command):
    def __init__(self):
        super().__init__(
            name="test",
            help="Run project tests.\n\nAvailable operations:\n- run: Run tests once\n- watch: Run tests in watch mode\n\nExample: craftsmanship test run"
        )
    
    def execute(self, operation: str = "run", ctx: Optional[DisplayContext] = None):
        """Execute the test command with the given operation."""
        result = effect.attempt(test, operation)
        if isinstance(result, Error):
            console.print(f"[red]Error: {result.error}[/red]")
            return
        return result.ok
