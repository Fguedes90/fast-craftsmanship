"""File utilities."""

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

import typer

from expression import Error, Ok, Option, Result, effect, pipe, result
from expression.collections import Block, Map

from fcship.tui import console

A = str
E = str
T = str
ValidationResult = Result
FileContent = tuple[Path, str]
RawFileContent = tuple[str, str]


@dataclass(frozen=True)
class FileError:
    message: str
    path: str


FileResult = Result


class FileStatus(NamedTuple):
    path: str
    status: str


@dataclass(frozen=True)
class FileCreationTracker:
    files: Map[str, str] = field(default_factory=Map.empty)

    def add_file(
        self, path: str, status: str = "Created"
    ) -> Result["FileCreationTracker", FileError]:
        return Ok(FileCreationTracker(self.files.add(path, status)))


@dataclass(frozen=True)
class FileOperation:
    path: Path
    content: str


def ensure_directory(path: Path) -> Result[None, FileError]:
    """Ensure directory exists."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        return Ok(None)
    except Exception as e:
        return Error(FileError(f"Failed to create directory: {path.parent}", str(e)))


def write_file(path: Path, content: str) -> Result[None, FileError]:
    """Write content to file."""
    # Ensure parent directory exists
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        console.print(f"[blue]Debug: Created parent directory: {path.parent}[/blue]")
    except Exception as e:
        console.print(f"[red]Error creating directory {path.parent}: {e!s}[/red]")
        return Error(FileError(f"Failed to create directory: {path.parent}", str(e)))

    # Write file content
    try:
        console.print(f"[blue]Debug: Writing content to file: {path}[/blue]")
        path.write_text(content)
        console.print(f"[blue]Debug: Successfully wrote content to file: {path}[/blue]")
        return Ok(None)
    except Exception as e:
        console.print(f"[red]Error writing file {path}: {e!s}[/red]")
        return Error(FileError(f"Failed to write file: {path}", str(e)))


@effect.result[FileCreationTracker, str]()
def create_single_file(tracker, path_content: FileContent):
    """Create a single file."""
    rel_path, content = path_content
    if not isinstance(rel_path, Path):
        rel_path = Path(rel_path)

    console.print(f"[blue]Debug: Creating file {rel_path}[/blue]")

    if isinstance(tracker, Path):
        file_path = rel_path if rel_path.is_absolute() else tracker / rel_path
        write_result = write_file(file_path, content)
        if write_result.is_error():
            yield Error(write_result.error)
            return
        yield Ok(FileOperation(file_path, content))
    elif isinstance(tracker, FileCreationTracker):
        # Create the file
        write_result = write_file(rel_path, content)
        if write_result.is_error():
            yield Error(write_result.error)
            return

        console.print(f"[blue]Debug: Adding file to tracker: {rel_path!s}[/blue]")
        add_result = tracker.add_file(str(rel_path))
        if add_result.is_error():
            yield Error(str(add_result.error))
            return
        yield Ok(add_result.ok)
    else:
        yield Error(FileError("Invalid tracker type", ""))


def build_file_path(base: Path, file_info: RawFileContent) -> FileContent:
    return (base / file_info[0], file_info[1])


def process_all_files(base: Path, files: Map[str, str], tracker: FileCreationTracker) -> FileResult:
    return files.fold(
        lambda acc, item: pipe(
            acc, result.bind(lambda tr: create_single_file(tr, build_file_path(base, item)))
        ),
        Ok(tracker),
    )


@effect.result[FileCreationTracker, FileError]()
def create_files(files: Map[str, str], base_path: str = ""):
    yield pipe(
        Ok(Path(base_path)),
        result.bind(lambda base: process_all_files(base, files, FileCreationTracker())),
    )


def format_error_message(msg: str, value: str = "") -> str:
    return f"{msg}{f': {value}' if value else ''}"


def create_validation_error(msg: str) -> Result[None, typer.BadParameter]:
    return Error(typer.BadParameter(msg))


def check(condition: bool, msg: str) -> ValidationResult:
    return Ok(None) if condition else Error(typer.BadParameter(msg))


def validate_name_requirement(
    operation: str, requires_name: Block[str], name: str | None
) -> ValidationResult:
    return check(
        not (operation in requires_name and not name), f"Operation '{operation}' requires name"
    )


def validate_operation_existence(valid_ops: Block[str], operation: str) -> ValidationResult:
    return check(operation in valid_ops, f"Invalid operation: {operation}")


def bind_name_validation(
    requires_name: Block[str], name: str | None, operation: str
) -> Callable[[Result[None, typer.BadParameter]], Result[None, typer.BadParameter]]:
    return lambda _: validate_name_requirement(operation, requires_name, name)


def validate_operation(
    valid_ops: Block[str], requires_name: Block[str], operation: str, name: str | None
) -> Result[None, typer.BadParameter]:
    return validate_operation_existence(valid_ops, operation).bind(
        lambda _: validate_name_requirement(operation, requires_name, name)
    )


def find_file_in_tracker(tracker: FileCreationTracker, path: str) -> Option[str]:
    return pipe(
        tracker.files,
        lambda files: files.filter(lambda fs: fs.path == path),
        lambda filtered: filtered.map(lambda fs: fs.status),
    )


def init_file_creation_tracker() -> Result[FileCreationTracker, FileError]:
    return Ok(FileCreationTracker())


def file_creation_status(tracker: FileCreationTracker) -> str:
    return f"Created files: {list(tracker.files.keys())}"


__all__ = [
    "FileError",
    "FileOperation",
    "create_files",
    "create_single_file",
    "ensure_directory",
    "file_creation_status",
    "init_file_creation_tracker",
    "validate_operation",
    "write_file",
]
