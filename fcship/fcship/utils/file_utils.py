from pathlib import Path
from typing import Optional, Callable, TypeVar, Tuple
import typer
from expression import Result, Ok, Error, Option, Some, Nothing, pipe, result
from expression.collections import Map, Block

A = TypeVar('A')
E = TypeVar('E')

FileContent = Tuple[Path, str]
RawFileContent = Tuple[str, str]

from typing import NamedTuple
from dataclasses import dataclass

class FileStatus(NamedTuple):
    path: str
    status: str

ValidationResult = Result[None, typer.BadParameter]

@dataclass(frozen=True)
class FileError:
    message: str
    path: str

@dataclass(frozen=True)
class FileCreationTracker:
    files: Block[FileStatus] = Block.empty()

    def add_file(self, path: str, status: str = "Created") -> Result["FileCreationTracker", FileError]:
        return Ok(FileCreationTracker(self.files.cons(FileStatus(path, status))))




from expression.core import try_

@try_[FileError]()
def ensure_directory(path: Path) -> Result[None, FileError]:
    path.parent.mkdir(parents=True, exist_ok=True)

@try_[FileError]()
def write_file(path: Path, content: str) -> Result[None, FileError]:
    path.write_text(content)


def create_single_file(tracker: FileCreationTracker, path_content: FileContent) -> Result[FileCreationTracker, FileError]:
    path, content = path_content
    
    return pipe(
        ensure_directory(path),
        result.bind(lambda _: write_file(path, content)),
        result.bind(lambda _: tracker.add_file(str(path)))
    )

def build_file_path(base: Path, file_info: RawFileContent) -> FileContent:
    path, content = file_info
    return base / path, content



def process_all_files(base: Path, files: Block[RawFileContent], tracker: FileCreationTracker) -> Result[FileCreationTracker, FileError]:
    return files.fold(
        lambda acc, item: acc.bind(lambda tr: create_single_file(tr, build_file_path(base, item))),
        Ok(tracker)
    )

def create_files(files: Map[str, str], base_path: str = "") -> Result[FileCreationTracker, FileError]:
    base = Path(base_path)
    tracker = FileCreationTracker()
    return process_all_files(base, files, tracker)

def format_error_message(msg: str, value: str = "") -> str:
    return f"{msg}{(': ' + value) if value else ''}"

def create_validation_error(msg: str) -> Result[None, typer.BadParameter]:
    return Error(typer.BadParameter(msg))

def check(condition: bool, msg: str) -> ValidationResult:
    return Ok(None) if condition else Error(typer.BadParameter(msg))

def validate_name_requirement(operation: str, requires_name: Block[str], name: Optional[str]) -> ValidationResult:
    return check(not (operation in requires_name and not name), f"Operation '{operation}' requires name")

def validate_operation_existence(valid_ops: Block[str], operation: str) -> ValidationResult:
    return check(operation in valid_ops, f"Invalid operation: {operation}")

def bind_name_validation(requires_name: Block[str], name: Optional[str], operation: str) -> Callable[[Result[None, typer.BadParameter]], Result[None, typer.BadParameter]]:
    return lambda _: validate_name_requirement(operation, requires_name, name)

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
    
    return checks.traverse(
        lambda check: Ok() if check[0] else Error(typer.BadParameter(check[1]))).map(lambda _: None)
    

def find_file_in_tracker(tracker: FileCreationTracker, path: str) -> Option[str]:
    """Pure: Find a file's status in the tracker."""
    return tracker.files.filter(lambda fs: fs.path == path).map(lambda fs: fs.status)
