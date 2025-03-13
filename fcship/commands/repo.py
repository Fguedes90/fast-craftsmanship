"""Repository command implementation."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import typer
from expression import Error, Ok, Result, effect
from expression.collections import Map
from fcship.templates.repo_templates import get_repo_templates
from fcship.tui import DisplayContext
from fcship.utils import (
    FileCreationTracker,
    console,
    create_single_file,
    ensure_directory,
    success_message,
)
from .base import Command

@dataclass(frozen=True)
class RepoContext:
    """Immutable context for repository creation"""
    name: str
    files: Map[str, str]

@effect.result[str, str]()
def validate_repo_name(name: str):
    """Validate repository name"""
    name = name.strip()
    if not name:
        yield Error("Repository name cannot be empty")
    elif not name.isidentifier():
        yield Error("Repository name must be a valid Python identifier")
    else:
        yield Ok(name)

@effect.result[RepoContext, str]()
def prepare_repo_files(name: str):
    """Prepare repository files from templates"""
    try:
        files = get_repo_templates(name)
        files_map = Map.empty()
        for path, content in files.items():
            files_map = files_map.add(path, content)
        yield Ok(RepoContext(name=name, files=files_map))
    except Exception as e:
        yield Error(f"Failed to prepare repository files: {e!s}")

@effect.result[None, str]()
def ensure_repo_directories():
    """Ensure repository directories exist"""
    try:
        directories = [Path("infrastructure/repositories")]
        for directory in directories:
            result = ensure_directory(directory)
            if result.is_error():
                yield Error(f"Failed to create repository directories: {result.error}")
                return
        yield Ok(None)
    except Exception as e:
        yield Error(f"Failed to create repository directories: {e!s}")

@effect.result[FileCreationTracker, str]()
def create_repo_files(ctx: RepoContext):
    """Create repository files on disk"""
    try:
        dir_result = yield from ensure_repo_directories()
        if dir_result.is_error():
            yield Error(dir_result.error)
            return

        tracker = FileCreationTracker()
        for path, content in ctx.files.items():
            result = yield from create_single_file(tracker, (Path(path), content))
            if result.is_error():
                yield Error(result.error)
                return
            tracker = result.ok
        yield Ok(tracker)
    except Exception as e:
        yield Error(f"Failed to create repository files: {e!s}")

@effect.result[str, str]()
def create_repo(name: str):
    """Create new repository files."""
    try:
        name_result = yield from validate_repo_name(name)
        if name_result.is_error():
            yield Error(name_result.error)
            return

        context_result = yield from prepare_repo_files(name_result.ok)
        if context_result.is_error():
            yield Error(context_result.error)
            return

        tracker_result = yield from create_repo_files(context_result.ok)
        if tracker_result.is_error():
            yield Error(tracker_result.error)
            return

        msg = f"Created repository {name}"
        display_ctx = DisplayContext(console=console)
        notify_result = yield from success_message(display_ctx, msg)
        if notify_result.is_error():
            yield Error(notify_result.error)
            return

        yield Ok(msg)
    except Exception as e:
        yield Error(f"Unexpected error: {e!s}")

@effect.result[tuple[str, str], str]()
def validate_operation(operation: str, name: str):
    """Validate repository operation"""
    if operation == "create":
        yield Ok((operation, name))
    else:
        yield Error(f"Invalid operation '{operation}'. Supported operations: [create]")

@effect.result[str, str]()
def repo(
    operation: str = typer.Argument("create", help="Operation to perform [create]"),
    name: str = typer.Argument(..., help="Name of the repository"),
) -> Result[str, str]:
    """Create new repository files."""
    try:
        operation_result = yield from validate_operation(operation, name)
        if operation_result.is_error():
            yield Error(operation_result.error)
            return

        _, repo_name = operation_result.ok
        result = yield from create_repo(repo_name)
        if result.is_error():
            yield Error(result.error)
            return

        yield Ok(result.ok)
    except Exception as e:
        yield Error(f"Unexpected error: {e!s}")

class RepoCommand(Command):
    def __init__(self):
        super().__init__(
            name="repo",
            help="Create and manage repositories.\n\nAvailable operations:\n- create: Create a new repository\n\nExample: craftsmanship repo create user"
        )
    
    def execute(self, operation: str = "create", name: Optional[str] = None, ctx: Optional[DisplayContext] = None):
        """Execute the repository command with the given operation and name."""
        if not name:
            self.display_info()
            return
            
        result = effect.attempt(repo, operation, name)
        if isinstance(result, Error):
            console.print(f"[red]Error: {result.error}[/red]")
            return
        return result.ok
