from collections.abc import Callable
from pathlib import Path
import typer
from expression import Result, Ok, Error, Option, Some, Nothing, Try, pipe, result
from expression.collections import Map, Block
from expression.core import try_
from typing import NamedTuple
from dataclasses import dataclass, field

A = type("A")
E = type("E")
T = type("T")
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
    files: Block[FileStatus] = field(default_factory=Block.empty)

    def add_file(self, path: str, status: str = "Created") -> Result["FileCreationTracker", FileError]:
        return Ok(FileCreationTracker(self.files.cons(FileStatus(path, status))))

@dataclass(frozen=True)
class FileOperation:
    path: Path
    content: str



def ensure_directory(path: Path) -> FileResult:
    return Try(
        path.parent.mkdir(parents=True, exist_ok=True), 
        FileError(f"Failed to create directory: {path.parent}", str(path.parent)))


def write_file(path: Path, content: str) -> FileResult:
    return Try(path.write_text(content), FileError(f"Failed to write file: {path}", str(path)))


def create_single_file(tracker, path_content: FileContent) -> FileResult:
    rel_path, content = path_content
    if isinstance(tracker, Path):
        file_path = tracker / rel_path if not rel_path.is_absolute() else rel_path
        return pipe(
            ensure_directory(file_path),
            result.bind(lambda _: write_file(file_path, content)),
            result.bind(lambda _: Ok(FileOperation(file_path, content)))
        )
    elif isinstance(tracker, FileCreationTracker):
        return pipe(
            ensure_directory(rel_path),
            result.bind(lambda _: write_file(rel_path, content)),
            result.bind(lambda _: tracker.add_file(str(rel_path)))
        )
    else:
        return Error(FileError("Invalid tracker type", ""))

def build_file_path(base: Path, file_info: RawFileContent) -> FileContent:
    return (base / file_info[0], file_info[1])



def process_all_files(base: Path, files: Block[RawFileContent], tracker: FileCreationTracker) -> FileResult:
    return files.fold(
        lambda acc, item: pipe(
            acc,
            result.bind(lambda tr: create_single_file(tr, build_file_path(base, item)))
        ),
        Ok(tracker)
    )

def create_files(files: Map[str, str], base_path: str = "") -> FileResult:
    return pipe(
        Ok(Path(base_path)),
        result.bind(lambda base: process_all_files(base, files, FileCreationTracker()))
    )

def format_error_message(msg: str, value: str = "") -> str:
    return f"{msg}{f': {value}' if value else ''}"

def create_validation_error(msg: str) -> Result[None, typer.BadParameter]:
    return Error(typer.BadParameter(msg))

def check(condition: bool, msg: str) -> ValidationResult:
    return Ok(None) if condition else Error(typer.BadParameter(msg))

def validate_name_requirement(operation: str, requires_name: Block[str], name: str | None) -> ValidationResult:
    return check(not (operation in requires_name and not name), f"Operation '{operation}' requires name")

def validate_operation_existence(valid_ops: Block[str], operation: str) -> ValidationResult:
    return check(operation in valid_ops, f"Invalid operation: {operation}")

def bind_name_validation(requires_name: Block[str], name: str | None, operation: str) -> Callable[[Result[None, typer.BadParameter]], Result[None, typer.BadParameter]]:
    return lambda _: validate_name_requirement(operation, requires_name, name)

def validate_operation(
    valid_ops: Block[str],
    requires_name: Block[str],
    operation: str,
    name: str | None
) -> Result[None, typer.BadParameter]:
    return validate_operation_existence(valid_ops, operation).bind(
        lambda _: validate_name_requirement(operation, requires_name, name)
    )
    

def find_file_in_tracker(tracker: FileCreationTracker, path: str) -> Option[str]:
    return pipe(
        tracker.files,
        lambda files: files.filter(lambda fs: fs.path == path),
        lambda filtered: filtered.map(lambda fs: fs.status)
    )
