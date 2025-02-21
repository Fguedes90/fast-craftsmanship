"""File handling utilities."""
from collections.abc import Generator
from pathlib import Path
from rich.console import Console
from rich.live import Live
from rich.table import Table
from contextlib import contextmanager
from expression import Try, effect

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
    
    with Live(
        tracker.make_table(),
        console=console,
        refresh_per_second=4,
    ) as live:
        try:
            yield tracker
            live.update(tracker.make_table())
        finally:
            live.update(tracker.make_table())

@effect.try_[None]()
def create_file(path: Path, content: str, status_tracker: FileCreationTracker) -> None:
    """Create a single file with content."""
    ensure_directory(path)
    path.write_text(content)
    status_tracker.add_file(str(path))

def create_files(files: dict[str, str], base_path: str = "") -> None:
    """Create multiple files with their contents.
    
    Args:
        files: Dictionary mapping file paths to their contents
        base_path: Optional base path to prepend to all file paths
    """
    with file_creation_status() as status:
        for path, content in files.items():
            full_path = Path(base_path) / path
            Try.apply(lambda: create_file(full_path, content, status))
