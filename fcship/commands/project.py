"""Project initialization command using Railway Oriented Programming."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import typer

from expression import Error, Ok, effect, tagged_union
from expression.collections import Block, Map
from rich.console import Console
from rich.panel import Panel

from fcship.templates.project_templates import get_project_templates
from fcship.tui.display import DisplayContext, error_message, success_message
from fcship.utils.error_handling import handle_command_errors


@tagged_union
class ProjectError:
    """Tagged union for project command errors."""

    tag: Literal["validation_error", "file_error", "template_error"]
    validation_error: str | None = None
    file_error: tuple[str, str] | None = None
    template_error: str | None = None

    @staticmethod
    def ValidationError(message: str) -> "ProjectError":
        """Creates a validation error."""
        return ProjectError(tag="validation_error", validation_error=message)

    @staticmethod
    def FileError(path: str, details: str) -> "ProjectError":
        """Creates a file operation error."""
        return ProjectError(tag="file_error", file_error=(path, details))

    @staticmethod
    def TemplateError(message: str) -> "ProjectError":
        """Creates a template generation error."""
        return ProjectError(tag="template_error", template_error=message)


@dataclass(frozen=True)
class ProjectContext:
    """Immutable context for project creation."""

    name: str
    root_path: Path
    folders: Block[str]
    templates: Map[str, str]  # Maps relative file path to content


@dataclass(frozen=True)
class FileCreationResult:
    """Immutable result of file creation operation."""

    path: Path
    is_directory: bool = False


@dataclass(frozen=True)
class FileCreationTracker:
    """Tracks created files."""

    files: list[FileCreationResult] = None

    def __post_init__(self):
        object.__setattr__(self, "files", self.files or [])

    def add_file(self, result: FileCreationResult) -> "FileCreationTracker":
        """Add a file to the tracker."""
        return FileCreationTracker(files=self.files + [result])


@effect.result[str, ProjectError]()
def validate_project_operation(operation: str):
    """Validate the project operation."""
    valid_operations = ["init"]

    if operation not in valid_operations:
        yield Error(
            ProjectError.ValidationError(
                f"Invalid operation '{operation}'. Must be one of: {', '.join(valid_operations)}"
            )
        )
        return

    yield Ok(operation)


@effect.result[str, ProjectError]()
def validate_project_name(name: str):
    """Validate the project name."""
    name = name.strip()

    if not name:
        yield Error(ProjectError.ValidationError("Project name cannot be empty"))
        return

    if " " in name:
        yield Error(ProjectError.ValidationError("Project name cannot contain spaces"))
        return

    if not all(c.isalnum() or c in "-_" for c in name):
        yield Error(
            ProjectError.ValidationError(
                "Project name must contain only alphanumeric characters, hyphens, or underscores"
            )
        )
        return

    yield Ok(name)


@effect.result[ProjectContext, ProjectError]()
def prepare_project_context(name: str):
    """Prepare project context with templates and folder structure."""
    try:
        # Define standard project folders
        folders = Block.of_seq(
            [
                "domain",
                "service",
                "api/v1",
                "api/schemas",
                "infrastructure/repositories",
                "tests/unit",
                "tests/integration",
                "tests/api",
            ]
        )

        # Get project templates
        templates_dict = get_project_templates(name)

        # Convert to Map
        templates_map = Map.empty()
        for path, content in templates_dict.items():
            templates_map = templates_map.add(path, content)

        # Create context
        yield Ok(
            ProjectContext(
                name=name, root_path=Path(name), folders=folders, templates=templates_map
            )
        )
    except Exception as e:
        yield Error(ProjectError.TemplateError(f"Failed to generate project templates: {e!s}"))


@effect.result[FileCreationResult, ProjectError]()
def create_project_directory(ctx: ProjectContext, folder: str):
    """Create a single project directory."""
    try:
        # Create path
        dir_path = ctx.root_path / folder

        # Create directory
        dir_path.mkdir(parents=True, exist_ok=True)

        yield Ok(FileCreationResult(path=dir_path, is_directory=True))
    except Exception as e:
        yield Error(
            ProjectError.FileError(
                str(ctx.root_path / folder), f"Failed to create directory: {e!s}"
            )
        )


@effect.result[FileCreationResult, ProjectError]()
def create_project_file(ctx: ProjectContext, file_path: str, content: str):
    """Create a single project file."""
    try:
        # Create full path
        full_path = ctx.root_path / file_path

        # Ensure parent directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        full_path.write_text(content)

        yield Ok(FileCreationResult(path=full_path))
    except Exception as e:
        yield Error(
            ProjectError.FileError(str(ctx.root_path / file_path), f"Failed to write file: {e!s}")
        )


@effect.result[FileCreationTracker, ProjectError]()
def create_project_directories(ctx: ProjectContext):
    """Create all project directories."""
    try:
        tracker = FileCreationTracker()

        # Process each folder
        for folder in ctx.folders:
            # Create directory
            result = yield from create_project_directory(ctx, folder)
            if result.is_error():
                yield Error(result.error)
                return

            # Update tracker
            tracker = tracker.add_file(result.ok)

        yield Ok(tracker)
    except Exception as e:
        yield Error(
            ProjectError.FileError(
                str(ctx.root_path), f"Failed to create project directories: {e!s}"
            )
        )


@effect.result[FileCreationTracker, ProjectError]()
def create_project_files(ctx: ProjectContext):
    """Create all project files."""
    try:
        tracker = FileCreationTracker()

        # Process each file
        for file_path, content in ctx.templates.items():
            # Create file
            result = yield from create_project_file(ctx, file_path, content)
            if result.is_error():
                yield Error(result.error)
                return

            # Update tracker
            tracker = tracker.add_file(result.ok)

        yield Ok(tracker)
    except Exception as e:
        yield Error(
            ProjectError.FileError(str(ctx.root_path), f"Failed to create project files: {e!s}")
        )


@effect.result[str, ProjectError]()
def handle_project_error(error: ProjectError, ctx: DisplayContext = None):
    """Handle project errors with proper UI feedback."""
    display_ctx = ctx or DisplayContext(console=Console())

    match error:
        case ProjectError(tag="validation_error") if error.validation_error is not None:
            yield from error_message(display_ctx, "Validation Error", error.validation_error)
        case ProjectError(tag="file_error") if error.file_error is not None:
            path, details = error.file_error
            yield from error_message(display_ctx, f"File Error: {path}", details)
        case ProjectError(tag="template_error") if error.template_error is not None:
            yield from error_message(display_ctx, "Template Error", error.template_error)
        case _:
            yield from error_message(display_ctx, "Unknown Error", "An unknown error occurred")

    yield Error(error)


@effect.result[None, ProjectError]()
def display_next_steps(name: str, display_ctx: DisplayContext):
    """Display next steps after project creation."""
    try:
        next_steps = f"""
1. [cyan]cd[/cyan] {name}
2. [cyan]python -m venv .venv && source .venv/bin/activate[/cyan]
3. [cyan]pip install -e ".[dev]"[/cyan]
4. Start creating your domains with: [green]craftsmanship domain create <name>[/green]
"""
        display_ctx.console.print(Panel(next_steps, title="[bold]Next Steps", border_style="green"))
        yield Ok(None)
    except Exception as e:
        yield Error(ProjectError.ValidationError(f"Failed to display next steps: {e!s}"))


@effect.result[str, ProjectError]()
def init_project(name: str, display_ctx: DisplayContext = None):
    """Initialize new project structure."""
    ctx = display_ctx or DisplayContext(console=Console())

    # Validate project name
    name_result = yield from validate_project_name(name)
    if name_result.is_error():
        yield from handle_project_error(name_result.error, ctx)
        return

    # Prepare project context
    context_result = yield from prepare_project_context(name_result.ok)
    if context_result.is_error():
        yield from handle_project_error(context_result.error, ctx)
        return

    # Create files and directories with status
    with ctx.console.status("Creating project structure..."):
        # Create directories
        dir_result = yield from create_project_directories(context_result.ok)
        if dir_result.is_error():
            yield from handle_project_error(dir_result.error, ctx)
            return

        # Create files
        file_result = yield from create_project_files(context_result.ok)
        if file_result.is_error():
            yield from handle_project_error(file_result.error, ctx)
            return

    # Show success message
    message = f"Initialized project {name}"
    yield from success_message(ctx, message)

    # Show next steps
    next_steps_result = yield from display_next_steps(name, ctx)
    if next_steps_result.is_error():
        yield from handle_project_error(next_steps_result.error, ctx)
        return

    yield Ok(message)


@handle_command_errors
@effect.result[str, ProjectError]()
def project(
    operation: str = typer.Argument(..., help="Operation to perform [init]"),
    name: str = typer.Argument(..., help="Name of the project"),
    ctx: DisplayContext = None,
):
    """Initialize new project with basic structure."""
    display_ctx = ctx or DisplayContext(console=Console())

    # Validate operation
    op_result = yield from validate_project_operation(operation)
    if op_result.is_error():
        yield from handle_project_error(op_result.error, display_ctx)
        return

    # Execute operation
    if operation == "init":
        result = yield from init_project(name, display_ctx)
        if result.is_error():
            yield from handle_project_error(result.error, display_ctx)
            return

        yield Ok(result.ok)
    else:
        yield Error(ProjectError.ValidationError(f"Unsupported operation: {operation}"))
        return
