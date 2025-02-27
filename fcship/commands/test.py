"""Test command implementation using Railway Oriented Programming."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import typer

from expression import Error, Ok, effect, tagged_union
from rich.console import Console

from fcship.templates.test_templates import get_test_template
from fcship.tui.display import DisplayContext, error_message, success_message
from fcship.utils.error_handling import handle_command_errors
from fcship.utils.file_utils import ensure_directory, write_file


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


@effect.result[str, TestError]()
def validate_test_operation(operation: str):
    """Validate the test operation."""
    valid_operations = ["create"]

    if operation not in valid_operations:
        yield Error(
            TestError.ValidationError(
                f"Invalid operation '{operation}'. Must be one of: {', '.join(valid_operations)}"
            )
        )
        return

    yield Ok(operation)


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


@effect.result[str, TestError]()
def create_test(test_type: str, name: str, display_ctx: DisplayContext = None):
    """Create test files."""
    ctx = display_ctx or DisplayContext(console=Console())

    # Validate test type
    type_result = yield from validate_test_type(test_type)
    if type_result.is_error():
        yield from handle_test_error(type_result.error, ctx)
        return

    # Prepare test context
    context_result = yield from prepare_test_context(test_type, name)
    if context_result.is_error():
        yield from handle_test_error(context_result.error, ctx)
        return

    # Ensure directory exists
    dir_result = yield from ensure_test_directory(context_result.ok)
    if dir_result.is_error():
        yield from handle_test_error(dir_result.error, ctx)
        return

    # Write test file
    file_result = yield from write_test_file(context_result.ok, ctx)
    if file_result.is_error():
        yield from handle_test_error(file_result.error, ctx)
        return

    # Show success message
    message = f"Created {test_type} test {name}"
    yield from success_message(ctx, message)
    yield Ok(message)


@handle_command_errors
@effect.result[str, TestError]()
def test(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    test_type: str = typer.Argument(..., help="Type of test [unit/integration]"),
    name: str = typer.Argument(..., help="Name of the test"),
    ctx: DisplayContext = None,
):
    """Create test files based on type."""
    display_ctx = ctx or DisplayContext(console=Console())

    # Validate operation
    op_result = yield from validate_test_operation(operation)
    if op_result.is_error():
        yield from handle_test_error(op_result.error, display_ctx)
        return

    # Execute operation
    if operation == "create":
        result = yield from create_test(test_type, name, display_ctx)
        if result.is_error():
            yield from handle_test_error(result.error, display_ctx)
            return

        yield Ok(result.ok)
    else:
        yield Error(TestError.ValidationError(f"Unsupported operation: {operation}"))
        return
