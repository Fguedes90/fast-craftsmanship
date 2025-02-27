"""API command implementation."""

from dataclasses import dataclass
from pathlib import Path

import typer

from expression import Error, Ok, Result, effect
from expression.collections import Map

from fcship.templates.api_templates import get_api_templates
from fcship.tui import DisplayContext
from fcship.utils import (
    FileCreationTracker,
    console,
    create_single_file,
    ensure_directory,
    success_message,
)


@dataclass(frozen=True)
class ApiContext:
    """Immutable context for API creation"""

    name: str
    files: Map[str, str]


@effect.result[str, str]()
def validate_api_name(name: str):
    """Validate API name"""
    name = name.strip()
    if not name:
        yield Error("Invalid API name: name cannot be empty")
    elif not name.isidentifier():
        yield Error("Invalid API name: must be a valid Python identifier")
    else:
        yield Ok(name)


@effect.result[ApiContext, str]()
def prepare_api_files(name: str):
    """Prepare API files from templates"""
    try:
        files = get_api_templates(name)
        console.print(f"[blue]Debug: Generated templates for {name}:[/blue]")
        for path, content in files.items():
            console.print(f"[blue]  - {path}[/blue]")

        # Build Map by adding items one by one
        files_map = Map.empty()
        for path, content in files.items():
            files_map = files_map.add(path, content)
        console.print(f"[blue]Debug: Files map items: {list(files_map.items())}[/blue]")

        yield Ok(ApiContext(name=name, files=files_map))
    except Exception as e:
        console.print(f"[red]Error preparing API files: {e!s}[/red]")
        yield Error(f"Failed to prepare API files: {e!s}")


@effect.result[None, str]()
def ensure_api_directories():
    """Ensure all required API directories exist"""
    try:
        # Create required directories
        directories = [Path("api"), Path("api/v1"), Path("api/schemas"), Path("tests/api")]

        console.print("[blue]Debug: Creating directories:[/blue]")
        for directory in directories:
            console.print(f"[blue]  - {directory}[/blue]")
            result = ensure_directory(directory)
            if result.is_error():
                yield Error(f"Failed to create API directories: {result.error}")
                return

        yield Ok(None)
    except Exception as e:
        yield Error(f"Failed to create API directories: {e!s}")


@effect.result[FileCreationTracker, str]()
def create_api_files(ctx: ApiContext):
    """Create API files on disk"""
    try:
        # Ensure API directories exist first
        dir_result = yield from ensure_api_directories()
        if dir_result.is_error():
            yield Error(dir_result.error)
            return

        console.print("[blue]Debug: Creating files:[/blue]")
        tracker = FileCreationTracker()

        # Debug: Print files to be created
        console.print(f"[blue]Debug: Files in context: {list(ctx.files.items())}[/blue]")

        # Iterate through each file and create it
        for path, content in ctx.files.items():
            console.print(f"[blue]Debug: Processing file {path}[/blue]")
            result = yield from create_single_file(tracker, (Path(path), content))
            if result.is_error():
                console.print(f"[red]Error creating file {path}: {result.error}[/red]")
                yield Error(result.error)
                return
            tracker = result.ok
            console.print(f"[blue]Debug: Successfully created file {path}[/blue]")

        console.print("[blue]Debug: Files created successfully[/blue]")
        yield Ok(tracker)
    except Exception as e:
        console.print(f"[red]Unexpected error in create_api_files: {e!s}[/red]")
        yield Error(f"Failed to create API files: {e!s}")


@effect.result[str, str]()
def notify_success(ctx: ApiContext, tracker: FileCreationTracker):
    """Notify about successful API creation"""
    try:
        msg = f"Created API endpoint {ctx.name}"
        display_ctx = DisplayContext(console=console)
        result = yield from success_message(display_ctx, msg)
        if result.is_error():
            yield Error(result.error)
            return
        yield Ok(msg)
    except Exception as e:
        yield Error(f"Failed to show success message: {e!s}")


@effect.result[str, str]()
def create_api(name: str):
    """Create new API endpoint files."""
    try:
        # Validate name
        name_result = yield from validate_api_name(name)
        if name_result.is_error():
            yield Error(name_result.error)
            return

        # Prepare files
        context_result = yield from prepare_api_files(name_result.ok)
        if context_result.is_error():
            yield Error(context_result.error)
            return

        # Create files
        tracker_result = yield from create_api_files(context_result.ok)
        if tracker_result.is_error():
            yield Error(tracker_result.error)
            return

        # Notify success
        notify_result = yield from notify_success(context_result.ok, tracker_result.ok)
        if notify_result.is_error():
            yield Error(notify_result.error)
            return

        yield Ok(notify_result.ok)
    except Exception as e:
        yield Error(f"Unexpected error: {e!s}")


@effect.result[tuple[str, str], str]()
def validate_operation(operation: str, name: str):
    """Validate API operation"""
    if operation == "create":
        yield Ok((operation, name))
    else:
        yield Error(f"Invalid operation '{operation}'. Supported operations: [create]")


@effect.result[str, str]()
def api(
    operation: str = typer.Argument("create", help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the API route"),
) -> Result[str, str]:
    """Create new API endpoint files."""
    # Validate operation
    try:
        operation_result = yield from validate_operation(operation, name)
    except Exception as exc:
        yield Error(str(exc))
        return

    if operation_result.is_error():
        yield Error(operation_result.error)
        return

    # Create API
    _, api_name = operation_result.ok
    try:
        result = yield from create_api(api_name)
    except Exception as e:
        yield Error(f"Unexpected error: {e!s}")
        return
    if result.is_error():
        yield Error(result.error)
        return

    yield Ok(result.ok)
