"""Shared utilities for CLI commands."""
from .file_utils import ensure_directory, FileCreationTracker, create_files, file_creation_status
from .validation import validate_operation
from .error_handling import handle_command_errors
from .ui import success_message, error_message
from .type_utils import ensure_type, map_type
from .functional import (
    catch_errors, 
    collect_results, 
    sequence_results, 
    tap, 
    tap_async, 
    lift_option,
)

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
]
