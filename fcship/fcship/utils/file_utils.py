"""File handling utilities."""
from collections.abc import Generator
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.table import Table
from contextlib import contextmanager
from expression import Try, effect, Result
import typer

console = Console()

@effect.try_[None]()
def ensure_directory(path: Path) -> None:
    """Garante que o diretório pai do caminho fornecido exista, criando-o se necessário."""
    path.parent.mkdir(parents=True, exist_ok=True)

class FileCreationTracker:
    """Track file creation progress and display it in a table."""
    def __init__(self):
        self.files: dict[str, str] = {}

    def add_file(self, path: str, status: str = "Created") -> None:
        """Add a file to track."""
        self.files[path] = status

    def make_table(self) -> Table:
        """Create a table showing file creation status."""
        table = Table()
        table.add_column("File")
        table.add_column("Status")

        for path, status in self.files.items():
            table.add_row(path, status)

        return table

@contextmanager
def file_creation_status(title: str = "Creating files...") -> Generator[FileCreationTracker, None, None]:
    """Context manager for tracking and displaying file creation status."""
    tracker = FileCreationTracker()

    with Live(tracker.make_table(), console=console, refresh_per_second=4) as live:
        try:
            yield tracker
        finally:
            live.update(tracker.make_table())

@effect.try_[None]()
def create_file(path: Path, content: str, status_tracker: FileCreationTracker) -> None:
    """Create a single file with content."""
    ensure_directory(path)
    path.write_text(content)
    status_tracker.add_file(str(path))

def create_files(files: dict[str, str], base_path: str = "") -> Result[None, Exception]:
    """Cria múltiplos arquivos e compõe os efeitos de forma funcional.

    Args:
        files: Dicionário que mapeia caminhos para conteúdos
        base_path: Caminho base a ser prefixado (opcional)

    Retorna:
        Result.ok(None) se todos os arquivos forem criados com sucesso,
        ou Result.error com o erro encontrado.
    """
    with file_creation_status() as status:
        results = [
            Try.apply(lambda: create_file(Path(base_path) / path, content, status))
            for path, content in files.items()
        ]
        return Result.sequence(results).map(lambda _: None)

def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None
) -> Result[str, Exception]:
    """Valida a operação e os argumentos de forma funcional.

    Retorna:
        Result.ok(operation) se válido ou Result.error com BadParameter se inválido.
    """
    if operation not in valid_operations:
        valid_ops = ", ".join(valid_operations)
        return Result.error(typer.BadParameter(f"Invalid operation: {operation}. Valid operations: {valid_ops}"))

    if requires_name and operation in requires_name and not name:
        return Result.error(typer.BadParameter(f"Operation '{operation}' requires a name parameter"))

    return Result.ok(operation)
