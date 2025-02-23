"""Terminal User Interface (TUI) components and utilities."""
from .types import (
    DisplayError,
    console,
    ConsoleProtocol
)

from .display import (
    DisplayResult,
    display_message,
    success_message,
    error_message,
    warning_message,
    display_rule,
    batch_display_messages,
    display_indented_text,
    handle_display
)

from .panels import (
    create_panel,
    create_nested_panel,
)

from .tables import (
    create_table_row,
    add_row_to_table,
    create_summary_table,
    format_message,
    create_multi_column_table,
    display_table,
)

from .input import (
    prompt_for_input,
    confirm_action,
)

from .progress import (
    display_progress,
    safe_display_with_progress,
    run_with_timeout,
)

from .extra import (
    with_fallback,
    with_retry,
    handle_ui_error,
    aggregate_errors,
    recover_ui,
    safe_display,
    with_ui_context
)

from .helpers import (
    validate_input,
    validate_style,
    validate_panel_inputs,
    validate_table_row,
    validate_table_data,
    validate_progress_inputs,
    is_valid_style,
    VALID_STYLES
)

__all__ = [
    # Types and core components
    "DisplayError",
    "DisplayResult",
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
    "VALID_STYLES"
]
