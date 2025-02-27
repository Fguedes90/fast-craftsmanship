"""Terminal User Interface (TUI) components and utilities."""

from .display import (
    DisplayContext,
    DisplayResult,
    batch_display_messages,
    display_indented_text,
    display_message,
    display_rule,
    error_message,
    handle_display,
    success_message,
    warning_message,
)
from .extra import (
    aggregate_errors,
    handle_ui_error,
    recover_ui,
    safe_display,
    with_fallback,
    with_retry,
    with_ui_context,
)
from .helpers import (
    VALID_STYLES,
    is_valid_style,
    validate_input,
    validate_panel_inputs,
    validate_progress_inputs,
    validate_style,
    validate_table_data,
    validate_table_row,
)
from .input import (
    confirm_action,
    prompt_for_input,
)
from .panels import (
    create_nested_panel,
    create_panel,
)
from .progress import (
    display_progress,
    run_with_timeout,
    safe_display_with_progress,
)
from .tables import (
    add_row_to_table,
    create_multi_column_table,
    create_summary_table,
    create_table_row,
    display_table,
    format_message,
)
from .types import ConsoleProtocol, DisplayError, console

__all__ = [
    # Types and core components
    "DisplayError",
    "DisplayResult",
    "DisplayContext",
    "ConsoleProtocol",
    "console",
    # Display functions
    "display_message",
    "success_message",
    "error_message",
    "warning_message",
    "display_rule",
    "batch_display_messages",
    "display_indented_text",
    "handle_display",
    "with_ui_context",
    # Panel functions
    "create_panel",
    "create_nested_panel",
    # Table functions
    "create_table_row",
    "add_row_to_table",
    "create_summary_table",
    "format_message",
    "create_multi_column_table",
    "display_table",
    # Input functions
    "prompt_for_input",
    "confirm_action",
    # Progress functions
    "display_progress",
    "safe_display_with_progress",
    "run_with_timeout",
    # Extra utilities
    "with_fallback",
    "with_retry",
    "handle_ui_error",
    "aggregate_errors",
    "recover_ui",
    "safe_display",
    # Helper functions
    "validate_input",
    "validate_style",
    "validate_panel_inputs",
    "validate_table_row",
    "validate_table_data",
    "validate_progress_inputs",
    "is_valid_style",
    "VALID_STYLES",
]
