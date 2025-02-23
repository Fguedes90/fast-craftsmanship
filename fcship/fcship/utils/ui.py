"""UI utilities for CLI output."""

import contextlib
from typing import TypeVar, Literal, TypeGuard, Any, TypeAlias
from collections.abc import Iterable, Callable
import typer
from expression import Result, Ok, Error, effect, Try, pipe, tagged_union
from expression.collections import seq, Block
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

T = TypeVar('T')
U = TypeVar('U')

@tagged_union
class DisplayError:
    """Represents display-related errors."""
    tag: Literal["validation", "rendering", "interaction"]
    validation: str | None = None
    rendering: tuple[str, Exception] | None = None
    interaction: tuple[str, Exception] | None = None

    @staticmethod
    def Validation(message: str) -> "DisplayError":
        """Create validation error."""
        return DisplayError(tag="validation", validation=message)

    @staticmethod
    def Rendering(message: str, error: Exception) -> "DisplayError":
        """Create rendering error."""
        return DisplayError(tag="rendering", rendering=(message, error))

    @staticmethod
    def Interaction(message: str, error: Exception) -> "DisplayError":
        """Create interaction error."""
        return DisplayError(tag="interaction", interaction=(message, error))

# Custom type aliases
DisplayResult: TypeAlias = Result[None, DisplayError]
TableResult: TypeAlias = Result[Table, DisplayError]
PanelResult: TypeAlias = Result[Panel, DisplayError]
ValidationResult: TypeAlias = Result[str, DisplayError]
TableRow: TypeAlias = tuple[str, str]
TableRowResult: TypeAlias = Result[TableRow, DisplayError]
TableData: TypeAlias = list[TableRow]
StyleValidator: TypeAlias = Callable[[str], ValidationResult]
DisplayFunction = Callable[[T], DisplayResult]
RecoveryStrategy: TypeAlias = dict[str, Callable[[], Result[T, DisplayError]]]
ProgressProcessor: TypeAlias = Callable[[T], Result[U, str]]

# Valid styles for Rich
VALID_STYLES = {"red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"}

# Validation functions
def is_valid_style(style: str) -> bool:
    """Check if a style string is valid for Rich."""
    return style in VALID_STYLES

def validate_style(style: str) -> ValidationResult:
    """Validate a style string."""
    return (validate_input(style, "Style")
            .bind(lambda s: Ok(s) if is_valid_style(s)
                  else Error(DisplayError.Validation(f"Invalid style: {s}. Must be one of: {', '.join(VALID_STYLES)}"))))

def is_table_row(value: Any) -> TypeGuard[tuple[str, str]]:
    """Type guard for table row tuple."""
    if not isinstance(value, tuple):
        return False
    if len(value) != 2:
        return False
    return all(isinstance(x, str) for x in value)

def validate_table_row(row: Any) -> TableRowResult:
    """Validate a table row."""
    if not is_table_row(row):
        return Error(DisplayError.Validation("Row must be a tuple of two strings"))
    return Ok(row)

def validate_table_data(headers: list[str], rows: TableData) -> DisplayResult:
    """Validate table headers and rows."""
    if not headers:
        return Error(DisplayError.Validation("Headers list cannot be empty"))
    if not all(isinstance(h, str) for h in headers):
        return Error(DisplayError.Validation("Headers must be strings"))
    if any(len(row) != len(headers) for row in rows):
        return Error(DisplayError.Validation("All rows must have same length as headers"))
    if not all(all(isinstance(cell, str) for cell in row) for row in rows):
        return Error(DisplayError.Validation("All cells must be strings"))
    return Ok(None)

def validate_panel_inputs(title: str, content: str, style: str) -> Result[tuple[str, str, str], DisplayError]:
    """Validate panel creation inputs."""
    return (validate_input(title, "Title")
            .bind(lambda t: validate_input(content, "Content")
                  .bind(lambda s: validate_style(style)
                        .map(lambda s: (t, content, s)))))

def validate_progress_inputs[T](
    items: Iterable[T],
    process_fn: ProgressProcessor[T, U],
    description: str,
) -> Result[None, DisplayError]:
    """Validate progress display inputs."""
    try:
        items_list = list(items)
        if not items_list:
            return Error(DisplayError.Validation("Items list cannot be empty"))
            
        if not callable(process_fn):
            return Error(DisplayError.Validation("Process function must be callable"))
            
        return validate_input(description, "Description").map(lambda _: None)
    except Exception as e:
        return Error(DisplayError.Validation(f"Invalid progress inputs: {str(e)}"))

console = Console()

def validate_input(value: str | None, name: str) -> ValidationResult:
    """Validates string input is not empty."""
    if not value:
        return Error(DisplayError.Validation(f"{name} cannot be empty"))
    return Ok(value)

@effect.try_[None]()
def display_message(message: str, style: str) -> None:
    """Display a message with given style using Expression's Try effect."""
    if not message:
        raise ValueError("Message cannot be empty")
    console.print(f"[{style}]{message}[/{style}]")

# Update function signatures to use DisplayResult
def success_message(message: str) -> DisplayResult:
    """Display a success message."""
    return (validate_input(message, "Message")
            .bind(lambda m: Try.apply(lambda: display_message(m, "green"))
                  .map_error(lambda e: DisplayError.Rendering("Failed to display success message", e))))

def error_message(message: str, details: str | None = None) -> DisplayResult:
    """Display an error message with optional details."""
    return (validate_input(message, "Message")
            .bind(lambda m: Ok(f"{m}\n\n{details}" if details else m))
            .bind(lambda m: Try.apply(lambda: display_message(m, "red"))
                  .map_error(lambda e: DisplayError.Rendering("Failed to display error message", e))))

def create_table_row(name_result: tuple[str, Result[str, T]]) -> TableRowResult:
    """Creates a single table row from a result."""
    name, result = name_result
    return (validate_input(name, "Row name")
            .map(lambda n: (n.title(), 
                          "[green]✨ Passed[/green]" if result.is_ok() 
                          else "[red]❌ Failed[/red]")))

def add_row_to_table(table: Table, row: TableRow) -> TableResult:
    """Adds a row to the table in a functional way."""
    if not isinstance(table, Table):
        return Error(DisplayError.Validation("Invalid table object"))
    try:
        table.add_row(*row)
        return Ok(table)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to add row to table", e))

def create_panel(title: str, content: str, style: str) -> PanelResult:
    """Creates a panel with the given parameters."""
    return (validate_input(title, "Title")
            .bind(lambda t: validate_input(content, "Content")
                  .bind(lambda c: validate_input(style, "Style")
                        .map(lambda s: Panel(c, title=t, border_style=s)))))

def create_summary_table[T](results: Block[tuple[str, Result[str, T]]]) -> TableResult:
    """Creates a summary table of verification results."""
    if not isinstance(results, Block):
        return Error(DisplayError.Validation("Results must be a Block"))
    
    table = Table()
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    
    def add_row(acc: Result[Table, DisplayError], row: tuple[str, Result[str, T]]) -> TableResult:
        return acc.bind(lambda t: create_table_row(row).bind(lambda r: add_row_to_table(t, r)))
    
    return pipe(
        results,
        seq.fold(add_row, Ok(table))
    )

def format_message(parts: list[str], separator: str = "\n\n") -> ValidationResult:
    """Format multiple message parts into a single message."""
    if not isinstance(parts, list):
        return Error(DisplayError.Validation("Message parts must be a list"))

    if filtered_parts := list(filter(None, parts)):
        return Ok(separator.join(filtered_parts))
    else:
        return Error(DisplayError.Validation("At least one non-empty message part is required"))

def display_table(headers: list[str], rows: TableData, title: str | None = None) -> DisplayResult:
    """Display a table using Rich for formatting."""
    if not headers:
        return Error(DisplayError.Validation("Headers list cannot be empty"))
    if not all(isinstance(h, str) for h in headers):
        return Error(DisplayError.Validation("Headers must be strings"))
    
    def _display() -> None:
        table = Table(title=title) if title else Table()
        for header in headers:
            table.add_column(header)
        for row in rows:
            if len(row) != len(headers):
                raise ValueError(f"Row length {len(row)} does not match headers length {len(headers)}")
            table.add_row(*row)
        console.print(table)
    
    return Try.apply(_display).map_error(lambda e: DisplayError.Rendering("Failed to display table", e))

def confirm_action(prompt: str) -> Result[bool, DisplayError]:
    """Display a confirmation prompt and return the boolean result."""
    return (validate_input(prompt, "Prompt")
            .bind(lambda p: Try.apply(lambda: typer.confirm(p))
                  .map_error(lambda e: DisplayError.Interaction("Failed to get user confirmation", e))))

def display_rule(message: str, style: str = "blue") -> DisplayResult:
    """Display a horizontal rule with a centered message."""
    return (validate_input(message, "Message")
            .bind(lambda m: Try.apply(lambda: console.rule(m, style=style))
                  .map_error(lambda e: DisplayError.Rendering("Failed to display rule", e))))

def warning_message(message: str) -> DisplayResult:
    """Display a warning message with yellow style."""
    return (validate_input(message, "Message")
            .bind(lambda m: Try.apply(lambda: display_message(m, "yellow"))
                  .map_error(lambda e: DisplayError.Rendering("Failed to display warning", e))))

def batch_display_messages(messages: list[tuple[str, StyleValidator]]) -> DisplayResult:
    """Display multiple messages with their styles in sequence."""
    def display_single(msg_style: tuple[str, str]) -> DisplayResult:
        msg, style = msg_style
        return (validate_input(msg, "Message")
                .bind(lambda m: Try.apply(lambda: display_message(m, style))
                      .map_error(lambda e: DisplayError.Rendering(f"Failed to display message: {m}", e))))
    
    return pipe(
        messages,
        Block.of_seq,
        seq.traverse(display_single),
        Result.map(lambda _: None)
    )

def create_multi_column_table(
    columns: list[tuple[str, StyleValidator]],
    rows: TableData,
    title: str | None = None
) -> TableResult:
    """Create a table with multiple styled columns."""
    if not columns:
        return Error(DisplayError.Validation("Must provide at least one column"))
        
    try:
        table = Table(title=title) if title else Table()
        for header, style in columns:
            table.add_column(header, style=style)
            
        for row in rows:
            if len(row) != len(columns):
                raise ValueError(f"Row has {len(row)} values but table has {len(columns)} columns")
            table.add_row(*row)
            
        return Ok(table)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to create table", e))

def prompt_for_input(
    prompt: str,
    validator: StyleValidator | None = None
) -> ValidationResult:
    """Prompt for user input with optional validation."""
    return (validate_input(prompt, "Prompt")
            .bind(lambda p: Try.apply(lambda: input(p))
                  .map_error(lambda e: DisplayError.Interaction("Failed to get user input", e)))
            .bind(lambda value: 
                  validator(value) if validator 
                  else Ok(value)))

def display_indented_text(
    text: str, 
    indent: int = 2,
    style: StyleValidator | None = None
) -> DisplayResult:
    """Display text with specified indentation and optional style."""
    return (validate_input(text, "Text")
            .map(lambda t: "\n".join(" " * indent + line for line in t.splitlines()))
            .bind(lambda indented: Try.apply(
                lambda: console.print(indented, style=style) if style else console.print(indented)
            ).map_error(lambda e: DisplayError.Rendering("Failed to display indented text", e))))

def create_nested_panel(
    title: str,
    sections: list[tuple[str, str]],
    outer_style: str = "blue",
    inner_style: str = "cyan"
) -> PanelResult:
    """Create a panel containing nested panels for each section."""
    return (validate_input(title, "Title")
            .bind(lambda t: 
                  pipe(
                      sections,
                      Block.of_seq,
                      seq.traverse(lambda section:
                          create_panel(section[0], section[1], inner_style)
                      ),
                      Result.map(lambda panels: "\n".join(str(p) for p in panels)),
                      Result.bind(lambda content: create_panel(t, content, outer_style))
                  )))

def display_progress[T, U](
    items: Iterable[T],
    process_fn: ProgressProcessor[T, U],
    description: str = "Processing"
) -> DisplayResult:
    """Display progress while processing items."""
    from rich.progress import Progress
    
    try:
        with Progress() as progress:
            task = progress.add_task(description, total=len(list(items)))
            
            results = []
            for item in items:
                result = process_fn(item)
                if result.is_error():
                    console.print(f"[red]Error processing item: {result.error}[/red]")
                results.append(result)
                progress.advance(task)
                
            if any(r.is_error() for r in results):
                return Error(DisplayError.Validation("Some items failed to process"))
            return Ok(None)
            
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display progress", e))

def with_fallback[T](
    operation: Callable[[], Result[T, DisplayError]], 
    fallback: T,
    error_message: str | None = None
) -> T:
    """Execute a UI operation with fallback value on error."""
    try:
        result = operation()
        if result.is_ok():
            return result.ok

        if error_message:
            error_message_result = error_message(error_message)
            if error_message_result.is_error():
                console.print("[red]Failed to display error message[/red]")

        return fallback
    except Exception as e:
        if error_message:
            with contextlib.suppress(Exception):
                console.print(f"[red]{error_message}: {str(e)}[/red]")
        return fallback

def with_retry[T](
    operation: Callable[[], Result[T, DisplayError]],
    max_attempts: int = 3,
    delay: float = 1.0
) -> Result[T, DisplayError]:
    """Execute a UI operation with retry on failure."""
    from time import sleep

    for attempt in range(max_attempts):
        result = operation()
        if result.is_ok():
            return result

        if attempt < max_attempts - 1:
            with contextlib.suppress(Exception):
                warning_message(f"Operation failed, retrying in {delay} seconds...")
                sleep(delay)
    return result  # Return last error result

def handle_ui_error(error: DisplayError) -> DisplayResult:
    """Handle UI errors in a consistent way."""
    match error:
        case DisplayError(tag="validation", validation=msg):
            return display_message(f"Validation Error: {msg}", "red")
            
        case DisplayError(tag="rendering", rendering=(msg, exc)):
            return display_message(f"Display Error: {msg}\n{str(exc)}", "red")
            
        case DisplayError(tag="interaction", interaction=(msg, exc)):
            return display_message(f"Input Error: {msg}\n{str(exc)}", "red")
            
        case _:
            return Error(DisplayError.Validation("Unknown error type"))

def aggregate_errors(errors: Block[DisplayError]) -> DisplayError:
    """Combine multiple errors into a single validation error."""
    error_messages = []
    for error in errors:
        match error:
            case DisplayError(tag="validation", validation=msg):
                error_messages.append(msg)
            case DisplayError(tag="rendering", rendering=(msg, _)):
                error_messages.append(msg)
            case DisplayError(tag="interaction", interaction=(msg, _)):
                error_messages.append(msg)
    return DisplayError.Validation("\n".join(error_messages))

def recover_ui[T](
    operation: Callable[[], Result[T, DisplayError]],
    recovery_strategies: RecoveryStrategy[T],
    max_attempts: int = 3
) -> Result[T, DisplayError]:
    """Execute UI operation with type-specific recovery strategies."""
    attempt = 0
    last_error: DisplayError | None = None
    
    while attempt < max_attempts:
        result = operation()
        if result.is_ok():
            return result
            
        error = result.error
        last_error = error
        
        if error.tag in recovery_strategies:
            attempt += 1
            operation = recovery_strategies[error.tag]
        else:
            break
            
    return Error(last_error or DisplayError.Validation("Unknown error"))

def safe_display[T](
    content: T,
    display_fn: DisplayFunction[T],
    fallback_fn: DisplayFunction[T] | None = None
) -> DisplayResult:
    """Safely display content with fallback display function."""
    result = display_fn(content)
    if result.is_ok() or not fallback_fn:
        return result
        
    # Try fallback display on error
    return (fallback_fn(content)
            .map_error(lambda e: aggregate_errors(Block.of_seq([result.error, e]))))

def with_ui_context[T](
    operation: Callable[[], Result[T, DisplayError]],
    setup: DisplayFunction | None = None,
    cleanup: DisplayFunction | None = None
) -> Result[T, DisplayError]:
    """Run an operation with setup and cleanup."""
    try:
        if setup:
            setup_result = setup()
            if setup_result.is_error():
                return Error(setup_result.error)
                
        result = operation()
        
        if cleanup:
            cleanup_result = cleanup()
            if cleanup_result.is_error():
                return Error(cleanup_result.error)
                
        return result
    except ValueError as e:
        return Error(DisplayError.Validation(str(e)))
    except IOError as e:
        return Error(DisplayError.Rendering("IO operation failed", e))
    except TypeError as e:
        return Error(DisplayError.Validation(str(e)))
    except RuntimeError as e:
        return Error(DisplayError.Rendering("Operation failed", e))
