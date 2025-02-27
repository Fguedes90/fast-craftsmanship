"""Shared utilities for CLI commands."""

from rich.console import Console

from fcship.tui import error_message, success_message

from .error_handling import handle_command_errors
from .file_utils import (
    FileCreationTracker,
    FileError,
    create_files,
    create_single_file,
    ensure_directory,
    file_creation_status,
)
from .functional import (
    catch_errors,
    collect_results,
    lift_option,
    sequence_results,
    tap,
    tap_async,
)
from .type_utils import ensure_type, map_type
from .validation import validate_operation

# Create console instance for global use
console = Console()

__all__ = [
    "FileCreationTracker",
    "FileError",
    "catch_errors",
    "collect_results",
    "console",
    "create_files",
    "create_single_file",
    "ensure_directory",
    "ensure_type",
    "error_message",
    "file_creation_status",
    "handle_command_errors",
    "lift_option",
    "map_type",
    "sequence_results",
    "success_message",
    "tap",
    "tap_async",
    "validate_operation",
]
