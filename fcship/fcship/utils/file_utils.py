"""Pure file handling utilities."""
from pathlib import Path
from typing import Optional, Callable, TypeVar, Sequence, Tuple, Any
import typer
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from expression import Result, Ok, Error, Option, Some, Nothing, pipe
from expression.collections import Map, Block
from functools import reduce

A = TypeVar('A')
E = TypeVar('E')

from dataclasses import dataclass

@dataclass(frozen=True)
class FileError:
    """Immutable error representation for file operations."""
    message: str
    path: str

@dataclass(frozen=True)
class FileCreationTracker:
    """Immutable tracker of file creation progress."""
    files: Block[tuple[str, str]] = Block.empty()

    def add_file(self, path: str, status: str = "Created") -> Result["FileCreationTracker", FileError]:
        """Pure: Create new tracker with added file entry."""
        return Ok(FileCreationTracker(self.files.cons((path, status))))

def init_file_creation_tracker() -> Result[FileCreationTracker, FileError]:
    """Pure: Initialize empty file creation tracker."""
    return Ok(FileCreationTracker())

def create_directory_operation(path: Path) -> Callable[[], None]:
    """Pure: Create a directory creation operation."""
    def operation() -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
    return operation

def write_content_operation(path: Path, content: str) -> Callable[[], None]:
    """Pure: Create a file writing operation."""
    def operation() -> None:
        path.write_text(content)
    return operation

from expression.core import try_

@try_[FileError]()
def ensure_directory(path: Path) -> Result[None, FileError]:
    path.parent.mkdir(parents=True, exist_ok=True)

@try_[FileError]()
def write_file(path: Path, content: str) -> Result[None, FileError]:
    path.write_text(content)


def create_single_file(
    tracker: FileCreationTracker,
    path_content: tuple[Path, str]
) -> Result[FileCreationTracker, FileError]:
    path, content = path_content
    
    return pipe(
        ensure_directory(path),
        result.bind(lambda _: write_file(path, content)),
        result.bind(lambda _: tracker.add_file(str(path)))
    )

def build_file_path(base: Path, file_info: Tuple[str, str]) -> Tuple[Path, str]:
    """Pure: Build full file path from base and file info."""
    path, content = file_info
    return (base / path, content)

def process_single_file(
    tracker: FileCreationTracker,
    base: Path,
    file_info: Tuple[str, str]
) -> Result[FileCreationTracker, FileError]:
    """Pure: Process a single file creation with base path."""
    return create_single_file(tracker, build_file_path(base, file_info))

def process_files_item(
    base: Path,
    acc: Result[FileCreationTracker, FileError],
    item: Tuple[str, str]
) -> Result[FileCreationTracker, FileError]:
    """Pure: Process a single files item in the reduce operation."""
    def bind_process_file(tracker: FileCreationTracker) -> Result[FileCreationTracker, FileError]:
        return process_single_file(tracker, base, item)
    return acc.bind(bind_process_file)

def process_all_files(
    base: Path,
    files: Block[tuple[str, str]],
    tracker: FileCreationTracker
) -> Result[FileCreationTracker, FileError]:
    build_path = lambda item: build_file_path(base, item)
    
    return pipe(
        files.map(build_path),
        result.traverse(lambda pc: create_single_file(FileCreationTracker(), pc)),
        result.map(lambda results: reduce(lambda acc, t: FileCreationTracker(acc.files + t.files), results, tracker))
    )

def create_files(
    files: Map[str, str],
    base_path: str = ""
) -> Result[FileCreationTracker, FileError]:
    base = Path(base_path)
    return init_file_creation_tracker().match(
        ok=lambda tracker: process_all_files(base, files, tracker),
        error=lambda e: Error(FileError(str(e), base_path))
    )

def format_error_message(msg: str, value: str = "") -> str:
    """Pure: Format error message with optional value."""
    return f"{msg}{f': {value}' if value else ''}"

def create_validation_error(msg: str) -> Result[None, typer.BadParameter]:
    """Pure: Create validation error with message."""
    return Error(typer.BadParameter(msg))

def validate_name_requirement(
    operation: str,
    requires_name: Block[str],
    name: Optional[str]
) -> Result[None, typer.BadParameter]:
    """Pure: Validate name requirement."""
    if operation in requires_name and not name:
        return create_validation_error(f"Operation '{operation}' requires name")
    return Ok(None)

def validate_operation_existence(
    valid_ops: Block[str],
    operation: str
) -> Result[None, typer.BadParameter]:
    """Pure: Validate that operation exists."""
    if operation not in valid_ops:
        return create_validation_error(format_error_message("Invalid operation", operation))
    return Ok(None)

def bind_name_validation(
    requires_name: Block[str],
    name: Optional[str],
    operation: str
) -> Callable[[Result[None, typer.BadParameter]], Result[None, typer.BadParameter]]:
    """Pure: Bind name validation to operation validation."""
    def validate(_: None) -> Result[None, typer.BadParameter]:
        return validate_name_requirement(operation, requires_name, name)
    return validate

def validate_operation(
    valid_ops: Block[str], 
    requires_name: Block[str], 
    operation: str, 
    name: Optional[str]
) -> Result[None, typer.BadParameter]:
    checks = Block.of(
        (operation in valid_ops, f"Invalid operation: {operation}"),
        (not (operation in requires_name and not name), "Name required")
    )
    
    return pipe(
        checks,
        result.traverse(lambda check: Ok() if check[0] else Error(typer.BadParameter(check[1]))),
        result.map(lambda _: None)
    )

def find_file_in_tracker(tracker: FileCreationTracker, path: str) -> Option[str]:
    """Pure: Find a file's status in the tracker."""
    return tracker.files.find(lambda x: x[0] == path).map(lambda x: x[1])
