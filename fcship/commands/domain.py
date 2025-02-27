"""Domain command implementation using Railway Oriented Programming."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import typer

from expression import Error, Ok, effect, tagged_union
from expression.collections import Map
from rich.console import Console

from fcship.templates.domain_templates import get_domain_templates
from fcship.tui.display import DisplayContext, error_message, success_message
from fcship.utils.error_handling import handle_command_errors
from fcship.utils.file_utils import ensure_directory, write_file


@tagged_union
class DomainError:
    """Tagged union for domain command errors."""

    tag: Literal["validation_error", "file_error", "template_error"]
    validation_error: str | None = None
    file_error: tuple[str, str] | None = None
    template_error: str | None = None

    @staticmethod
    def ValidationError(message: str) -> "DomainError":
        """Creates a validation error."""
        return DomainError(tag="validation_error", validation_error=message)

    @staticmethod
    def FileError(path: str, details: str) -> "DomainError":
        """Creates a file operation error."""
        return DomainError(tag="file_error", file_error=(path, details))

    @staticmethod
    def TemplateError(message: str) -> "DomainError":
        """Creates a template generation error."""
        return DomainError(tag="template_error", template_error=message)


@dataclass(frozen=True)
class DomainContext:
    """Immutable context for domain creation."""

    name: str
    files: Map[str, str]  # Maps relative file path to content


@dataclass(frozen=True)
class FileCreationTracker:
    """Tracks created files."""

    files: list[Path] = None

    def __post_init__(self):
        object.__setattr__(self, "files", self.files or [])

    def add_file(self, path: Path) -> "FileCreationTracker":
        """Add a file to the tracker."""
        return FileCreationTracker(files=self.files + [path])


@effect.result[str, DomainError]()
def validate_domain_operation(operation: str):
    """Validate the domain operation."""
    valid_operations = ["create"]

    if operation not in valid_operations:
        yield Error(
            DomainError.ValidationError(
                f"Invalid operation '{operation}'. Must be one of: {', '.join(valid_operations)}"
            )
        )
        return

    yield Ok(operation)


@effect.result[str, DomainError]()
def validate_domain_name(name: str):
    """Validate the domain name."""
    name = name.strip()

    if not name:
        yield Error(DomainError.ValidationError("Domain name cannot be empty"))
        return

    if not name.isidentifier():
        yield Error(DomainError.ValidationError("Domain name must be a valid Python identifier"))
        return

    yield Ok(name)


@effect.result[DomainContext, DomainError]()
def prepare_domain_context(name: str):
    """Prepare domain context with templates."""
    try:
        # Get templates
        files_dict = get_domain_templates(name)

        # Convert to Map
        files_map = Map.empty()
        for path, content in files_dict.items():
            files_map = files_map.add(path, content)

        # Create context
        yield Ok(DomainContext(name=name, files=files_map))
    except Exception as e:
        yield Error(DomainError.TemplateError(f"Failed to generate domain templates: {e!s}"))


@effect.result[Path, DomainError]()
def create_domain_file(domain_name: str, file_path: str, content: str):
    """Create a single domain file."""
    try:
        # Create full path
        full_path = Path(f"domain/{domain_name}") / file_path

        # Ensure directory exists
        dir_result = yield from ensure_directory(full_path.parent)
        if dir_result.is_error():
            yield Error(
                DomainError.FileError(
                    str(full_path.parent), f"Failed to create directory: {dir_result.error}"
                )
            )
            return

        # Write file
        write_result = yield from write_file(full_path, content)
        if write_result.is_error():
            yield Error(
                DomainError.FileError(str(full_path), f"Failed to write file: {write_result.error}")
            )
            return

        yield Ok(full_path)
    except Exception as e:
        yield Error(
            DomainError.FileError(f"domain/{domain_name}/{file_path}", f"Unexpected error: {e!s}")
        )


@effect.result[FileCreationTracker, DomainError]()
def create_domain_files(ctx: DomainContext):
    """Create all domain files."""
    try:
        tracker = FileCreationTracker()

        # Process each file
        for file_path, content in ctx.files.items():
            # Create file
            result = yield from create_domain_file(ctx.name, file_path, content)
            if result.is_error():
                yield Error(result.error)
                return

            # Update tracker
            tracker = tracker.add_file(result.ok)

        yield Ok(tracker)
    except Exception as e:
        yield Error(
            DomainError.FileError(f"domain/{ctx.name}", f"Failed to create domain files: {e!s}")
        )


@effect.result[str, DomainError]()
def handle_domain_error(error: DomainError, ctx: DisplayContext = None):
    """Handle domain errors with proper UI feedback."""
    display_ctx = ctx or DisplayContext(console=Console())

    match error:
        case DomainError(tag="validation_error") if error.validation_error is not None:
            yield from error_message(display_ctx, "Validation Error", error.validation_error)
        case DomainError(tag="file_error") if error.file_error is not None:
            path, details = error.file_error
            yield from error_message(display_ctx, f"File Error: {path}", details)
        case DomainError(tag="template_error") if error.template_error is not None:
            yield from error_message(display_ctx, "Template Error", error.template_error)
        case _:
            yield from error_message(display_ctx, "Unknown Error", "An unknown error occurred")

    yield Error(error)


@effect.result[str, DomainError]()
def create_domain(name: str, display_ctx: DisplayContext = None):
    """Create a new domain with all required files."""
    ctx = display_ctx or DisplayContext(console=Console())

    # Validate domain name
    name_result = yield from validate_domain_name(name)
    if name_result.is_error():
        yield from handle_domain_error(name_result.error, ctx)
        return

    # Prepare domain context
    context_result = yield from prepare_domain_context(name_result.ok)
    if context_result.is_error():
        yield from handle_domain_error(context_result.error, ctx)
        return

    # Create files with status
    with ctx.console.status("Creating domain files..."):
        files_result = yield from create_domain_files(context_result.ok)
        if files_result.is_error():
            yield from handle_domain_error(files_result.error, ctx)
            return

    # Show success message
    message = f"Created domain {name}"
    yield from success_message(ctx, message)
    yield Ok(message)


@handle_command_errors
@effect.result[str, DomainError]()
def domain(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the domain"),
    ctx: DisplayContext = None,
):
    """Create a new domain with all required files."""
    display_ctx = ctx or DisplayContext(console=Console())

    # Validate operation
    op_result = yield from validate_domain_operation(operation)
    if op_result.is_error():
        yield from handle_domain_error(op_result.error, display_ctx)
        return

    # Execute operation
    if operation == "create":
        result = yield from create_domain(name, display_ctx)
        if result.is_error():
            yield from handle_domain_error(result.error, display_ctx)
            return

        yield Ok(result.ok)
    else:
        yield Error(DomainError.ValidationError(f"Unsupported operation: {operation}"))
        return
