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

class FileError:
    """Pure: Represents a file operation error."""
    def __init__(self, message: str, path: str):
        self._message = message
        self._path = path
    
    @property
    def message(self) -> str:
        return self._message
    
    @property
    def path(self) -> str:
        return self._path

class FileCreationTracker(BaseModel):
    """Track file creation progress."""
    files: Annotated[Map[str, str], Field(default_factory=Map.empty)]

    model_config = {
        "frozen": True,
        "arbitrary_types_allowed": True
    }

    def add_file(self, path: str, status: str = "Created") -> Result["FileCreationTracker", FileError]:
        return pipe(
            self.model_copy(update={"files": self.files.add(path, status)}),
            Ok,
            match(
                Ok, lambda tracker: Ok(tracker),
                Error, lambda e: Error(FileError(str(e), path))
            )
        )

def init_file_creation_tracker() -> Result[FileCreationTracker, FileError]:
    return pipe(
        FileCreationTracker(),
        Ok,
        match(
            Ok, lambda tracker: Ok(tracker),
            Error, lambda e: Error(FileError(str(e), ""))
        )
    )

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

def handle_io_error(e: Exception, path: str) -> FileError:
    """Pure: Convert IO exception to FileError."""
    return FileError(str(e), path)

def execute_io_operation(operation: Callable[[], None], path: str) -> Result[None, FileError]:
    return pipe(
        operation,
        Ok,
        match(
            Ok, lambda _: Ok(None),
            Error, lambda e: Error(handle_io_error(e, path))
        )
    )

def handle_io_operation(operation: Callable[[], None], path: str) -> Result[None, FileError]:
    return pipe(
        operation,
        Ok,
        match(
            Ok, lambda _: Ok(None),
            Error, lambda e: Error(FileError(str(e), path))
        )
    )

def ensure_directory(path: Path) -> Result[None, FileError]:
    """Pure: Ensure directory exists."""
    return handle_io_operation(lambda: path.parent.mkdir(parents=True, exist_ok=True), str(path.parent))

def write_file(path: Path, content: str) -> Result[None, FileError]:
    """Pure: Write content to file."""
    return handle_io_operation(lambda: path.write_text(content), str(path))

def bind_write_operation(path: Path, content: str) -> Callable[[Result[None, FileError]], Result[None, FileError]]:
    """Pure: Bind write operation to previous result."""
    def bind_operation(_: None) -> Result[None, FileError]:
        return write_file(path, content)
    return bind_operation

def bind_tracker_update(tracker: FileCreationTracker, path: str) -> Callable[[Result[None, FileError]], Result[FileCreationTracker, FileError]]:
    """Pure: Bind tracker update to previous result."""
    def bind_operation(_: None) -> Result[FileCreationTracker, FileError]:
        return tracker.add_file(path)
    return bind_operation

def create_single_file(
    tracker: FileCreationTracker,
    path_content: tuple[Path, str]
) -> Result[FileCreationTracker, FileError]:
    """Pure: Create a single file and update tracker."""
    path, content = path_content
    return pipe(
        ensure_directory(path),
        match(
            Ok, lambda _: write_file(path, content),
            Error, lambda e: Error(e)
        ),
        match(
            Ok, lambda _: tracker.add_file(str(path)),
            Error, lambda e: Error(e)
        )
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
    files: Map[str, str],
    tracker: FileCreationTracker
) -> Result[FileCreationTracker, FileError]:
    """Pure: Process all files in the map."""
    def process_item(acc: Result[FileCreationTracker, FileError], item: Tuple[str, str]) -> Result[FileCreationTracker, FileError]:
        return acc.bind(lambda t: create_single_file(t, build_file_path(base, item)))
    return reduce(process_item, files.items(), Ok(tracker))

def create_files(
    files: Map[str, str],
    base_path: str = ""
) -> Result[FileCreationTracker, FileError]:
    base = Path(base_path)
    return pipe(
        init_file_creation_tracker(),
        match(
            Ok, lambda tracker: process_all_files(base, files, tracker),
            Error, lambda e: Error(FileError(str(e), base_path))
        )
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
    """Pure: Validate operation and name combination."""
    return pipe(
        validate_operation_existence(valid_ops, operation),
        bind_name_validation(requires_name, name, operation)
    )

def find_file_in_tracker(tracker: FileCreationTracker, path: str) -> Option[str]:
    """Pure: Find a file's status in the tracker."""
    return Some(tracker.files[path]) if path in tracker.files else Nothing
