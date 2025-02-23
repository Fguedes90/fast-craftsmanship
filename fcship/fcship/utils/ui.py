"""UI utilities for CLI output."""
from dataclasses import dataclass
from typing import TypeVar, Literal, Callable, Iterable, TypeGuard, Any
import typer
from expression import Result, Ok, Error, effect, Try, pipe, tagged_union
from expression.collections import seq, Block
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

T = TypeVar('T')

# Validation functions
def is_valid_style(style: str) -> bool:
    """Check if a style string is valid for Rich."""
    valid_styles = {"red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"}
    return style in valid_styles

def validate_style(style: str) -> Result[str, DisplayError]:
    """Validate a style string."""
    return (validate_input(style, "Style")
            .bind(lambda s: Ok(s) if is_valid_style(s)
                  else Error(DisplayError.Validation(f"Invalid style: {s}. Must be one of: {', '.join(valid_styles)}"))))

def is_table_row(value: Any) -> TypeGuard[tuple[str, str]]:
    """Type guard for table row tuple."""
    return (isinstance(value, tuple) 
            and len(value) == 2 
            and all(isinstance(x, str) for x in value))

def validate_table_row(row: Any) -> Result[tuple[str, str], DisplayError]:
    """Validate a table row."""
    if not is_table_row(row):
        return Error(DisplayError.Validation("Row must be a tuple of two strings"))
    return Ok(row)

def validate_table_data(headers: list[str], rows: list[list[str]]) -> Result[None, DisplayError]:
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
                  .bind(lambda c: validate_style(style)
                        .map(lambda s: (t, c, s)))))

def validate_progress_inputs[T](
    items: Iterable[T],
    process_fn: Callable[[T], Result[str, str]],
    description: str
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

console = Console()

def validate_input(value: str | None, name: str) -> Result[str, DisplayError]:
    """Validates string input is not empty."""
    if not value:
        return Error(DisplayError.Validation(f"{name} cannot be empty"))
    return Ok(value)

@effect.try_[None]()
def display_message(message: str, style: str) -> None:
    """Display a message with given style using Expression's Try effect."""
    validation = validate_input(message, "Message")
    if validation.is_error():
        raise ValueError(str(validation.error))
        
    try:
        console.print(Panel(message, style=style))
    except Exception as e:
        raise ValueError(f"Failed to display message: {e}")

def success_message(message: str) -> Result[None, DisplayError]:
    """Display a success message."""
    return (validate_input(message, "Message")
            .bind(lambda m: Try.apply(lambda: display_message(m, "green"))
                  .map_error(lambda e: DisplayError.Rendering("Failed to display success message", e))))

def error_message(message: str, details: str | None = None) -> Result[None, DisplayError]:
    """Display an error message with optional details."""
    return (validate_input(message, "Message")
            .bind(lambda m: Ok(f"{m}\n\n{details}" if details else m))
            .bind(lambda m: Try.apply(lambda: display_message(m, "red"))
                  .map_error(lambda e: DisplayError.Rendering("Failed to display error message", e))))

def create_table_row[T](name_result: tuple[str, Result[str, T]]) -> Result[tuple[str, str], DisplayError]:
    """Creates a single table row from a result."""
    name, result = name_result
    return (validate_input(name, "Row name")
            .map(lambda n: (n.title(), 
                          "[green]✨ Passed[/green]" if result.is_ok() 
                          else "[red]❌ Failed[/red]")))

def add_row_to_table(table: Table, row: tuple[str, str]) -> Result[Table, DisplayError]:
    """Adds a row to the table in a functional way."""
    if not isinstance(table, Table):
        return Error(DisplayError.Validation("Invalid table object"))
        
    try:
        table.add_row(*row)
        return Ok(table)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to add row to table", e))

def create_panel(title: str, content: str, style: str) -> Result[Panel, DisplayError]:
    """Creates a panel with the given parameters."""
    return (validate_input(title, "Title")
            .bind(lambda t: validate_input(content, "Content")
                  .bind(lambda c: validate_input(style, "Style")
                        .map(lambda s: Panel(c, title=t, border_style=s)))))

def create_summary_table[T](results: Block[tuple[str, Result[str, T]]]) -> Result[Table, DisplayError]:
    """Creates a summary table of verification results."""
    if not isinstance(results, Block):
        return Error(DisplayError.Validation("Results must be a Block"))
        
    table = Table()
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="bold")
    
    def add_row(acc: Result[Table, DisplayError], row: tuple[str, Result[str, T]]) -> Result[Table, DisplayError]:
        return (acc.bind(lambda t: create_table_row(row)
                        .bind(lambda r: add_row_to_table(t, r))))
    
    return pipe(
        results,
        seq.fold(add_row, Ok(table))
    )

def format_message(parts: list[str], separator: str = "\n\n") -> Result[str, DisplayError]:
    """Format multiple message parts into a single message."""
    if not isinstance(parts, list):
        return Error(DisplayError.Validation("Parts must be a list"))

    if filtered_parts := list(filter(None, parts)):
        return Ok(separator.join(filtered_parts))
    else:
        return Error(DisplayError.Validation("No valid message parts provided"))

def display_table(headers: list[str], rows: list[list[str]], title: str | None = None) -> Result[None, DisplayError]:
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

def display_rule(message: str, style: str = "blue") -> Result[None, DisplayError]:
    """Display a horizontal rule with a centered message."""
    return (validate_input(message, "Message")
            .bind(lambda m: Try.apply(lambda: console.rule(m, style=style))
                  .map_error(lambda e: DisplayError.Rendering("Failed to display rule", e))))

def warning_message(message: str) -> Result[None, DisplayError]:
    """Display a warning message with yellow style."""
    return (validate_input(message, "Message")
            .bind(lambda m: Try.apply(lambda: display_message(m, "yellow"))
                  .map_error(lambda e: DisplayError.Rendering("Failed to display warning", e))))

def batch_display_messages(messages: list[tuple[str, str]]) -> Result[None, DisplayError]:
    """Display multiple messages with their styles in sequence.
    
    Args:
        messages: List of (message, style) tuples
    """
    def display_single(msg_style: tuple[str, str]) -> Result[None, DisplayError]:
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
    columns: list[tuple[str, str | None]],
    rows: list[list[str]],
    title: str | None = None
) -> Result[Table, DisplayError]:
    """Create a table with multiple styled columns.
    
    Args:
        columns: List of (header, style) tuples, style can be None
        rows: List of row values
        title: Optional table title
    """
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
    validator: None | (Callable[[str], Result[str, str]]) = None
) -> Result[str, DisplayError]:
    """Prompt for user input with optional validation.
    
    Args:
        prompt: The prompt to display
        validator: Optional function to validate input
    """
    return (validate_input(prompt, "Prompt")
            .bind(lambda p: Try.apply(lambda: input(p))
                  .map_error(lambda e: DisplayError.Interaction("Failed to get user input", e)))
            .bind(lambda value: 
                  validator(value).map_error(DisplayError.Validation) if validator 
                  else Ok(value)))

def display_indented_text(
    text: str, 
    indent: int = 2,
    style: str | None = None
) -> Result[None, DisplayError]:
    """Display text with specified indentation and optional style.
    
    Args:
        text: The text to display
        indent: Number of spaces to indent
        style: Optional style to apply
    """
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
) -> Result[Panel, DisplayError]:
    """Create a panel containing nested panels for each section.
    
    Args:
        title: Main panel title
        sections: List of (title, content) tuples for inner panels
        outer_style: Style for outer panel
        inner_style: Style for inner panels
    """
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

def display_progress[T](
    items: Iterable[T],
    process_fn: Callable[[T], Result[str, str]],
    description: str = "Processing"
) -> Result[None, DisplayError]:
    """Display progress while processing items.
    
    Args:
        items: Items to process
        process_fn: Function to process each item
        description: Description of the progress operation
    """
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
    """Execute a UI operation with fallback value on error.
    
    Args:
        operation: The UI operation to attempt
        fallback: Value to return if operation fails
        error_message: Optional error message to display on failure
    
    Returns:
        The operation result or fallback value
    """
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
            try:
                console.print(f"[red]{error_message}: {str(e)}[/red]")
            except:
                pass
        return fallback

def with_retry[T](
    operation: Callable[[], Result[T, DisplayError]],
    max_attempts: int = 3,
    delay: float = 1.0
) -> Result[T, DisplayError]:
    """Execute a UI operation with retry on failure.
    
    Args:
        operation: The UI operation to attempt
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    
    Returns:
        The operation result or final error
    """
    from time import sleep
    
    for attempt in range(max_attempts):
        result = operation()
        if result.is_ok():
            return result
            
        if attempt < max_attempts - 1:
            try:
                warning_message(f"Operation failed, retrying in {delay} seconds...")
                sleep(delay)
            except:
                pass
                
    return result  # Return last error result

def handle_ui_error(error: DisplayError) -> Result[None, DisplayError]:
    """Handle a UI error appropriately based on its type.
    
    Args:
        error: The DisplayError to handle
    
    Returns:
        Result indicating if error was handled successfully
    """
    match error:
        case DisplayError(tag="validation", validation=msg):
            return error_message(f"Validation Error: {msg}")
            
        case DisplayError(tag="rendering", rendering=(msg, exc)):
            return error_message(
                "Display Error",
                f"{msg}\nDetails: {str(exc)}"
            )
            
        case DisplayError(tag="interaction", interaction=(msg, exc)):
            return error_message(
                "Input Error",
                f"{msg}\nDetails: {str(exc)}"
            )
            
        case _:
            return error_message("Unknown Error", str(error))

def aggregate_errors(errors: Block[DisplayError]) -> DisplayError:
    """Aggregate multiple display errors into a single error.
    
    Args:
        errors: Block of display errors to aggregate
    
    Returns:
        Single DisplayError combining all error messages
    """
    def format_error(error: DisplayError) -> str:
        match error:
            case DisplayError(tag="validation", validation=msg):
                return f"- Validation: {msg}"
            case DisplayError(tag="rendering", rendering=(msg, exc)):
                return f"- Display: {msg} ({exc})"
            case DisplayError(tag="interaction", interaction=(msg, exc)):
                return f"- Input: {msg} ({exc})"
            case _:
                return f"- Unknown: {error}"

    formatted = pipe(
        errors,
        seq.map(format_error),
        seq.to_list
    )
    
    return DisplayError.Validation("\n".join(formatted))

def recover_ui[T](
    operation: Callable[[], Result[T, DisplayError]],
    recovery_strategies: dict[str, Callable[[], Result[T, DisplayError]]],
    max_attempts: int = 3
) -> Result[T, DisplayError]:
    """Execute UI operation with type-specific recovery strategies.
    
    Args:
        operation: The UI operation to attempt
        recovery_strategies: Dict mapping error tags to recovery functions
        max_attempts: Maximum number of recovery attempts
        
    Returns:
        Operation result or final error after recovery attempts
    """
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
    display_fn: Callable[[T], Result[None, DisplayError]],
    fallback_fn: Callable[[T], Result[None, DisplayError]] | None = None
) -> Result[None, DisplayError]:
    """Safely display content with fallback display function.
    
    Args:
        content: Content to display
        display_fn: Primary display function
        fallback_fn: Optional fallback display function for errors
        
    Returns:
        Result of display operation
    """
    result = display_fn(content)
    if result.is_ok() or not fallback_fn:
        return result
        
    # Try fallback display on error
    return (fallback_fn(content)
            .map_error(lambda e: aggregate_errors(Block.of_seq([result.error, e]))))

def with_ui_context[T](
    operation: Callable[[], Result[T, DisplayError]],
    setup: Callable[[], Result[None, DisplayError]] | None = None,
    cleanup: Callable[[], Result[None, DisplayError]] | None = None
) -> Result[T, DisplayError]:
    """Execute UI operation with setup and cleanup.
    
    Args:
        operation: The main UI operation to perform
        setup: Optional setup function to run before operation
        cleanup: Optional cleanup function to run after operation
        
    Returns:
        Operation result
    """
    # Run setup if provided
    if setup:
        setup_result = setup()
        if setup_result.is_error():
            return Error(setup_result.error)
    
    try:
        # Run main operation
        result = operation()
        
        # Run cleanup if provided
        if cleanup:
            cleanup_result = cleanup()
            if cleanup_result.is_error():
                return Error(aggregate_errors(Block.of_seq([
                    cleanup_result.error,
                    result.error if result.is_error() else DisplayError.Validation("Operation succeeded but cleanup failed")
                ])))
                
        return result
        
    except Exception as e:
        if cleanup:
            try:
                cleanup()
            except:
                pass
        return Error(DisplayError.Rendering("Operation failed", e))
