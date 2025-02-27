"""Repository command implementation using Railway Oriented Programming."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import typer

from expression import Error, Ok, effect, tagged_union
from expression.collections import Map
from rich.console import Console

from fcship.templates.repo_templates import get_repo_templates
from fcship.tui.display import DisplayContext, error_message, success_message
from fcship.utils.error_handling import handle_command_errors
from fcship.utils.file_utils import ensure_directory, write_file


@tagged_union
class RepoError:
    """Tagged union for repository command errors."""

    tag: Literal["validation_error", "file_error", "template_error"]
    validation_error: str | None = None
    file_error: tuple[str, str] | None = None
    template_error: str | None = None

    @staticmethod
    def ValidationError(message: str) -> "RepoError":
        """Creates a validation error."""
        return RepoError(tag="validation_error", validation_error=message)

    @staticmethod
    def FileError(path: str, details: str) -> "RepoError":
        """Creates a file operation error."""
        return RepoError(tag="file_error", file_error=(path, details))

    @staticmethod
    def TemplateError(message: str) -> "RepoError":
        """Creates a template generation error."""
        return RepoError(tag="template_error", template_error=message)


@dataclass(frozen=True)
class RepoContext:
    """Immutable context for repository creation."""

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


@effect.result[str, RepoError]()
def validate_repo_operation(operation: str):
    """Validate the repository operation."""
    valid_operations = ["create"]

    if operation not in valid_operations:
        yield Error(
            RepoError.ValidationError(
                f"Invalid operation '{operation}'. Must be one of: {', '.join(valid_operations)}"
            )
        )
        return

    yield Ok(operation)


@effect.result[str, RepoError]()
def validate_repo_name(name: str):
    """Validate the repository name."""
    name = name.strip()

    if not name:
        yield Error(RepoError.ValidationError("Repository name cannot be empty"))
        return

    if not name.isidentifier():
        yield Error(RepoError.ValidationError("Repository name must be a valid Python identifier"))
        return

    yield Ok(name)


@effect.result[RepoContext, RepoError]()
def prepare_repo_context(name: str):
    """Prepare repository context with templates."""
    try:
        # Get templates
        files_dict = get_repo_templates(name)

        # Convert to Map
        files_map = Map.empty()
        for path, content in files_dict.items():
            files_map = files_map.add(path, content)

        # Create context
        yield Ok(RepoContext(name=name, files=files_map))
    except Exception as e:
        yield Error(RepoError.TemplateError(f"Failed to generate repository templates: {e!s}"))


@effect.result[Path, RepoError]()
def create_repo_file(file_path: str, content: str):
    """Create a single repository file."""
    try:
        # Create path object
        path = Path(file_path)

        # Ensure directory exists
        dir_result = ensure_directory(path.parent)
        if dir_result.is_error():
            yield Error(
                RepoError.FileError(
                    str(path.parent), f"Failed to create directory: {dir_result.error}"
                )
            )
            return

        # Write file
        write_result = write_file(path, content)
        if write_result.is_error():
            yield Error(
                RepoError.FileError(str(path), f"Failed to write file: {write_result.error}")
            )
            return

        yield Ok(path)
    except Exception as e:
        yield Error(RepoError.FileError(file_path, f"Unexpected error: {e!s}"))


@effect.result[FileCreationTracker, RepoError]()
def create_repo_files(ctx: RepoContext):
    """Create all repository files."""
    try:
        tracker = FileCreationTracker()

        # Process each file
        for file_path, content in ctx.files.items():
            # Create file
            result = yield from create_repo_file(file_path, content)
            if result.is_error():
                yield Error(result.error)
                return

            # Update tracker
            tracker = tracker.add_file(result.ok)

        yield Ok(tracker)
    except Exception as e:
        yield Error(RepoError.FileError("repository", f"Failed to create repository files: {e!s}"))


@effect.result[str, RepoError]()
def handle_repo_error(error: RepoError, ctx: DisplayContext = None):
    """Handle repository errors with proper UI feedback."""
    display_ctx = ctx or DisplayContext(console=Console())

    match error:
        case RepoError(tag="validation_error") if error.validation_error is not None:
            yield from error_message(display_ctx, "Validation Error", error.validation_error)
        case RepoError(tag="file_error") if error.file_error is not None:
            path, details = error.file_error
            yield from error_message(display_ctx, f"File Error: {path}", details)
        case RepoError(tag="template_error") if error.template_error is not None:
            yield from error_message(display_ctx, "Template Error", error.template_error)
        case _:
            yield from error_message(display_ctx, "Unknown Error", "An unknown error occurred")

    yield Error(error)


@effect.result[str, RepoError]()
def create_repo(name: str, display_ctx: DisplayContext = None):
    """Create repository implementation files."""
    ctx = display_ctx or DisplayContext(console=Console())

    # Validate repository name
    name_result = yield from validate_repo_name(name)
    if name_result.is_error():
        yield from handle_repo_error(name_result.error, ctx)
        return

    # Prepare repository context
    context_result = yield from prepare_repo_context(name_result.ok)
    if context_result.is_error():
        yield from handle_repo_error(context_result.error, ctx)
        return

    # Create files with status
    with ctx.console.status("Creating repository files..."):
        files_result = yield from create_repo_files(context_result.ok)
        if files_result.is_error():
            yield from handle_repo_error(files_result.error, ctx)
            return

    # Show success message
    message = f"Created repository {name}"
    yield from success_message(ctx, message)
    yield Ok(message)


@handle_command_errors
@effect.result[str, RepoError]()
def repo(
    operation: str = typer.Argument(..., help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the repository"),
    ctx: DisplayContext = None,
):
    """Create repository implementation files."""
    display_ctx = ctx or DisplayContext(console=Console())

    # Validate operation
    op_result = yield from validate_repo_operation(operation)
    if op_result.is_error():
        yield from handle_repo_error(op_result.error, display_ctx)
        return

    # Execute operation
    if operation == "create":
        result = yield from create_repo(name, display_ctx)
        if result.is_error():
            yield from handle_repo_error(result.error, display_ctx)
            return

        yield Ok(result.ok)
    else:
        yield Error(RepoError.ValidationError(f"Unsupported operation: {operation}"))
        return
