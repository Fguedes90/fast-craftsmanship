# UI Utilities

The UI utilities module provides a comprehensive set of tools for building consistent, type-safe, and functional command-line interfaces using Rich and Expression.

## Core Concepts

### Type Aliases

```python
# Basic UI Results
DisplayResult: TypeAlias = Result[None, DisplayError]
"""Result type for display operations that don't return a value."""

TableResult: TypeAlias = Result[Table, DisplayError]
"""Result type for operations that return a Rich Table."""

PanelResult: TypeAlias = Result[Panel, DisplayError]
"""Result type for operations that return a Rich Panel."""

ValidationResult: TypeAlias = Result[str, DisplayError]
"""Result type for string validation operations."""

# Data Structures
TableRow: TypeAlias = tuple[str, str]
"""Type for representing a table row with two columns."""

TableData: TypeAlias = list[TableRow]
"""Type for representing table data as a list of rows."""

# Function Types
StyleValidator: TypeAlias = Callable[[str], ValidationResult]
"""Type for style validation functions."""

DisplayFunction[T]: TypeAlias = Callable[[T], DisplayResult]
"""Type for display functions that return DisplayResult."""

RecoveryStrategy[T]: TypeAlias = dict[str, Callable[[], Result[T, DisplayError]]]
"""Type for mapping error types to recovery functions."""

ProgressProcessor[T, U]: TypeAlias = Callable[[T], Result[U, str]]
"""Type for processing items in a progress operation."""
```

### DisplayError

A tagged union type representing all possible UI-related errors:

```python
@tagged_union
class DisplayError:
    """Represents display-related errors."""
    tag: Literal["validation", "rendering", "interaction", "timeout", "execution", "input"]
    validation: str | None = None
    rendering: tuple[str, Exception] | None = None
    interaction: tuple[str, Exception] | None = None
    timeout: tuple[str, Exception] | None = None
    execution: tuple[str, str] | None = None
    input: tuple[str, str] | None = None
    
    # Static constructors for each error type
    @staticmethod
    def Validation(message: str) -> "DisplayError":
        return DisplayError(tag="validation", validation=message)
        
    # Other constructors omitted for brevity
```

### Result-based Error Handling

All UI functions return `Result[T, DisplayError]` for type-safe error handling:

```python
Result[None, DisplayError]  # For display operations
Result[Table, DisplayError] # For table creation
Result[Panel, DisplayError] # For panel creation
```

## Basic Display Functions

### Messages

```python
success_message(message: str) -> DisplayResult
error_message(message: str, details: str | None = None) -> DisplayResult
warning_message(message: str) -> DisplayResult
display_message(message: str, style: str) -> DisplayResult
```

### Panels and Rules

```python
create_panel(title: str, content: str, style: str) -> Result[Panel, DisplayError]
display_rule(message: str, style: str = "blue") -> DisplayResult
```

## Tables

### Basic Tables

```python
create_table_row(name_result: tuple[str, Result[str, T]]) -> Result[tuple[str, str], DisplayError]
add_row_to_table(table: Table, row: tuple[str, str]) -> Result[Table, DisplayError]
create_summary_table(results: Block[tuple[str, Result[str, T]]]) -> Result[Table, DisplayError]
```

### Advanced Tables

```python
create_multi_column_table(
    columns: list[tuple[str, str | None]],
    rows: list[list[str]],
    title: str | None = None
) -> Result[Table, DisplayError]
```

## Input Handling

```python
prompt_for_input(
    prompt: str,
    validator: Callable[[str], Result[str, str]] | None = None
) -> Result[str, DisplayError]

confirm_action(prompt: str) -> Result[bool, DisplayError]
```

## Progress Display

```python
display_progress[T](
    items: Iterable[T],
    process_fn: Callable[[T], Result[str, str]],
    description: str = "Processing"
) -> DisplayResult
```

## Error Handling Utilities

### Basic Error Handling

```python
handle_ui_error(error: DisplayError) -> DisplayResult
aggregate_errors(errors: Block[DisplayError]) -> DisplayError
```

### Advanced Error Recovery

```python
with_fallback[T](
    operation: Callable[[], Result[T, DisplayError]], 
    fallback: T,
    error_message: str | None = None
) -> T

with_retry[T](
    operation: Callable[[], Result[T, DisplayError]],
    max_attempts: int = 3,
    delay: float = 1.0
) -> Result[T, DisplayError]

recover_ui[T](
    operation: Callable[[], Result[T, DisplayError]],
    recovery_strategies: dict[str, Callable[[], Result[T, DisplayError]]],
    max_attempts: int = 3
) -> Result[T, DisplayError]
```

## Context Management

```python
with_ui_context[T](
    operation: Callable[[], Result[T, DisplayError]],
    setup: Callable[[], Result[None, DisplayError]] | None = None,
    cleanup: Callable[[], Result[None, DisplayError]] | None = None
) -> Result[T, DisplayError]
```

## Safe Display Operations

```python
safe_display[T](
    content: T,
    display_fn: Callable[[T], Result[None, DisplayError]],
    fallback_fn: Callable[[T], Result[None, DisplayError]] | None = None
) -> DisplayResult
```

## Validation

```python
def validate_input(value: str | None, name: str) -> Result[str, DisplayError]
def validate_style(style: str) -> Result[str, DisplayError]
def validate_table_data(headers: list[str], rows: list[list[str]]) -> Result[None, DisplayError]
```

## Best Practices

1. **Always Handle Errors**: Use `.map_error(handle_ui_error)` or proper error handling for all UI operations
2. **Validate Inputs**: Use validation functions before processing
3. **Use Type Safety**: Leverage generic types and Result for type-safe operations
4. **Compose Operations**: Use pipe and functional composition for complex operations
5. **Provide Context**: Use descriptive error messages and proper error types

## Examples

### Creating a Summary Display

```python
def display_summary(results: Block[tuple[str, Result[str, Error]]]) -> DisplayResult:
    return (
        create_summary_table(results)
        .bind(lambda table: 
            display_rule("Summary")
            .bind(lambda _: Ok(console.print(table)))
        )
    )
```

### Input with Validation

```python
def get_verified_input(prompt: str) -> Result[str, DisplayError]:
    return prompt_for_input(
        prompt,
        lambda value: Ok(value) if value.strip() else Error("Input cannot be empty")
    )
```

### Error Recovery

```python
def safe_display_operation() -> DisplayResult:
    return recover_ui(
        lambda: display_complex_ui(),
        {
            "rendering": lambda: display_fallback_ui(),
            "validation": lambda: display_error_message()
        }
    )
```

### Progress with Context

```python
def process_with_progress(items: list[str]) -> DisplayResult:
    return with_ui_context(
        lambda: display_progress(
            items,
            process_item,
            "Processing items"
        ),
        setup=lambda: display_rule("Starting Process"),
        cleanup=lambda: display_rule("Process Complete")
    )
```

## Common Usage Patterns

### Composing Multiple UI Operations

```python
def complex_ui_operation() -> DisplayResult:
    return (
        display_rule("Starting Operation")
        .bind(lambda _: prompt_for_input("Enter value: "))
        .bind(lambda value: 
            create_panel("Input", value, "cyan")
            .bind(lambda panel: Ok(console.print(panel)))
        )
        .bind(lambda _: success_message("Operation complete"))
    )
```

### Safe Error Recovery

When dealing with potentially failing UI operations:

```python
def display_with_recovery() -> None:
    result = with_retry(
        lambda: display_complex_data(),
        max_attempts=3,
        delay=1.0
    )
    
    if result.is_error():
        with_fallback(
            lambda: display_simple_fallback(),
            fallback=None,
            error_message="Failed to display data"
        )
```

### Progress with Error Handling

Processing items with progress and proper error handling:

```python
def process_items(items: list[str]) -> DisplayResult:
    return with_ui_context(
        lambda: display_progress(
            items,
            lambda item: Try.apply(lambda: process_single_item(item))
                .map_error(lambda e: f"Failed to process {item}: {str(e)}"),
            "Processing items"
        ),
        setup=lambda: display_rule("Starting batch process"),
        cleanup=lambda: display_rule("Process complete")
    )
```

## Terminal UI (TUI)

The Fast-Craftsmanship CLI includes an interactive Terminal User Interface (TUI) that provides a user-friendly way to navigate and use all available commands.

### Launching the TUI

The TUI can be launched with:

```bash
# Using the menu command
python -m fcship.cli menu

# From the Makefile
make tui
```

### TUI Features

- **Category-based Navigation**: Commands are organized into logical categories for easy navigation
- **Interactive Selection**: Select commands and options with simple keyboard input
- **Command Help**: View detailed help for any available command
- **Command Execution**: Run commands directly from the TUI with interactive input
- **Keyboard Navigation**: Use keyboard shortcuts for quick navigation (b for back, q for quit)
- **Context-aware Display**: See relevant information for each command
- **Error Handling**: Graceful error handling for command execution failures

### TUI Structure

The TUI provides a three-level navigation structure:

1. **Category Selection**: Choose from available command categories (scaffold, vcs, quality, db)
2. **Command Selection**: Select a specific command within the chosen category
3. **Command Options**: Run the command or view its help information

### Implementation Details

The TUI is implemented using the Rich library for Python:

```python
# Main TUI components
def run_tui() -> None:
    """Run the Terminal UI application."""
    try:
        while True:
            # Display categories and get selection
            valid_categories = display_categories()
            choice = Prompt.ask("> ", choices=["q"] + [str(i) for i in range(1, len(valid_categories) + 1)])
            
            if choice.lower() == 'q':
                break
                
            # Handle category, command, and option selection
            # [implementation details]
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Menu interrupted. Exiting...[/bold yellow]")
    finally:
        clear_screen()
        console.print("[bold green]Thanks for using Fast-Craftsmanship CLI![/bold green]")
```

### Menu Navigation Functions

The TUI implementation includes several key functions:

```python
# Display available categories
def display_categories():
    """Display the available command categories."""
    # Implementation using Rich tables and panels
    
# Display commands within a category
def display_commands(category_id: str):
    """Display the commands for a specific category."""
    # Implementation using Rich tables
    
# Display options for a command
def display_command_options(category_id: str, command_name: str):
    """Display options for a specific command."""
    # Implementation using Rich panels and tables
    
# Execute commands
def run_command(command_name: str, show_help: bool = False):
    """Run a command or show its help."""
    # Implementation using subprocess
```

### Command Execution

Commands are executed using Python's subprocess module to maintain interactive capabilities:

```python
def run_command(command_name: str, show_help: bool = False):
    """Run a command or show its help."""
    cmd = ["python", "-m", "fcship.cli", command_name, "--help" if show_help else ""]
    
    try:
        # Use subprocess.Popen to maintain interactive capabilities
        process = subprocess.Popen(cmd)
        process.wait()
        
        # Handle command completion or failure
        if process.returncode == 0:
            console.print("\n[bold green]Command completed successfully.[/bold green]")
        else:
            console.print(f"\n[bold red]Command failed with exit code {process.returncode}[/bold red]")
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
```

### Example Usage Flow

A typical user interaction flow:

1. Launch the TUI with `python -m fcship.cli menu`
2. View the available categories and select one (e.g., "scaffold")
3. View commands in the selected category and choose one (e.g., "project")
4. Choose to either run the command or view its help
5. If running the command, interact with it directly
6. After command execution, return to the command options menu
7. Navigate back to previous menus or quit the TUI

### Batch Operations with Progress

For commands that process multiple items with progress tracking:

```python
def batch_process[T, U](
    items: Block[T],
    process_fn: Callable[[T], Result[U, DisplayError]],
    batch_size: int = 10
) -> Result[Block[U], DisplayError]:
    def process_batch(batch: Block[T]) -> DisplayResult:
        return with_ui_context(
            lambda: display_progress(
                batch,
                process_fn,
                f"Processing batch of {len(batch)} items"
            ),
            setup=lambda: display_rule("Starting batch"),
            cleanup=lambda: success_message("Batch complete")
        )
    
    return pipe(
        items.chunk(batch_size),
        seq.traverse(process_batch),
        Result.map(seq.concat)
    )
```

### Form Input Collection

Collecting multiple inputs with validation:

```python
def collect_form_data(
    fields: list[tuple[str, Callable[[str], Result[str, str]]]]
) -> Result[dict[str, str], DisplayError]:
    def collect_field(field: tuple[str, Callable[[str], Result[str, str]]]) -> Result[tuple[str, str], DisplayError]:
        prompt, validator = field
        return prompt_for_input(f"{prompt}: ", validator).map(lambda v: (prompt, v))
    
    return pipe(
        fields,
        Block.of_seq,
        seq.traverse(collect_field),
        Result.map(dict)
    )
```

## Integration with Other Modules

### With Error Handling Module

```python
from fcship.utils.error_handling import handle_command_errors

@handle_command_errors
def safe_ui_operation() -> None:
    result = complex_ui_operation()
    if result.is_error():
        handle_ui_error(result.error)
```

### With Validation Module

```python
from fcship.utils.validation import validate_path

def prompt_for_file() -> Result[str, DisplayError]:
    return prompt_for_input(
        "Enter file path: ",
        lambda p: validate_path(p).map_error(str)
    )
```

### With Type Utils

```python
from fcship.utils.type_utils import ensure_type

def display_typed_data[T](data: Any, expected_type: type[T]) -> DisplayResult:
    return (
        ensure_type(data, expected_type)
        .map_error(lambda e: DisplayError.Validation(str(e)))
        .bind(lambda typed_data: display_message(str(typed_data), "cyan"))
    )
```

## Testing UI Components

### Mock Console Example

```python
from unittest.mock import Mock
from rich.console import Console

def test_ui_component():
    mock_console = Mock(spec=Console)
    result = with_ui_context(
        lambda: display_complex_ui(),
        console=mock_console
    )
    assert result.is_ok()
    mock_console.print.assert_called()
```

### Testing Error Handling

```python
def test_error_recovery():
    failing_op = lambda: Error(DisplayError.Rendering("Test error", Exception()))
    result = with_retry(failing_op, max_attempts=2)
    assert result.is_error()
    assert result.error.tag == "rendering"
```

## Performance Considerations

1. **Batch Processing**: Use `batch_process` for large datasets
2. **Progress Indicators**: Only use for operations taking >1 second
3. **Error Recovery**: Set reasonable retry attempts and delays
4. **Context Management**: Clean up resources properly with `with_ui_context`

## Extending the UI Utilities

### Creating Custom Display Types

```python
@dataclass
class CustomDisplay:
    title: str
    content: str
    style: str

def display_custom(
    custom: CustomDisplay
) -> DisplayResult:
    return create_panel(
        custom.title,
        custom.content,
        custom.style
    ).bind(lambda panel: Ok(console.print(panel)))
```

### Adding New Error Types

```python
@tagged_union
class CustomDisplayError(DisplayError):
    tag: Literal["validation", "rendering", "interaction", "timeout", "execution", "input", "custom"]
    custom: str | None = None

    @staticmethod
    def Custom(message: str) -> "CustomDisplayError":
        return CustomDisplayError(tag="custom", custom=message)
```

### Usage Examples

```python
# Using TableResult
def create_status_table(items: list[str]) -> TableResult:
    table = Table()
    table.add_column("Item")
    table.add_column("Status")
    for item in items:
        table.add_row(item, "✓")
    return Ok(table)

# Using DisplayFunction
def with_fallback_display[T](
    content: T,
    primary: DisplayFunction[T],
    fallback: DisplayFunction[T]
) -> DisplayResult:
    result = primary(content)
    return result if result.is_ok() else fallback(content)

# Using RecoveryStrategy
def with_recovery[T](operation: Callable[[], Result[T, DisplayError]]) -> Result[T, DisplayError]:
    strategies: RecoveryStrategy[T] = {
        "validation": lambda: retry_with_default(),
        "rendering": lambda: retry_with_simple_output(),
        "interaction": lambda: retry_with_alternate_input()
    }
    return recover_ui(operation, strategies)
```

## Future Improvements

1. **Keyboard Shortcuts**: Add more keyboard shortcuts for faster navigation
2. **Theming Support**: Allow users to customize the TUI appearance
3. **Command History**: Implement command history tracking
4. **Parameter Input**: Add interactive parameter input for commands
5. **Persistent Settings**: Save user preferences between sessions
6. **Help Context**: Show command help inline for better usability
7. **Auto-complete**: Add tab completion for command names and parameters
8. **Filter Options**: Allow filtering command lists by keyword