"""Shared utilities for CLI commands."""
from rich.console import Console
from .file_utils import (
    ensure_directory,
    FileCreationTracker,
    create_files,
    file_creation_status,
    FileError,
    create_single_file
)
from .validation import validate_operation
from .error_handling import handle_command_errors
from fcship.tui import success_message, error_message
from .type_utils import ensure_type, map_type
from .functional import (
    catch_errors, 
    collect_results, 
    sequence_results, 
    tap, 
    tap_async, 
    lift_option,
)

# Create console instance for global use
console = Console()

__all__ = [
    "ensure_directory",
    "FileCreationTracker",
    "create_files",
    "file_creation_status",
    "validate_operation",
    "handle_command_errors",
    "success_message",
    "error_message",
    "ensure_type",
    "map_type",
    "catch_errors",
    "collect_results",
    "sequence_results",
    "tap",
    "tap_async",
    "lift_option",
    "console",
    "FileError",
    "create_single_file"
]
