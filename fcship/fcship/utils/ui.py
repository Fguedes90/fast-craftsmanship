"""UI utilities for CLI output."""

import contextlib
from typing import TypeVar, Literal, TypeGuard, Any, TypeAlias, Optional, Sequence
from collections.abc import Iterable, Callable, Awaitable
import typer
from expression import Result, Ok, Error, effect, Try, pipe, Option, Some, Nothing
from expression.collections import seq, Block
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from .errors import DisplayError
import asyncio
from typing import Coroutine
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from contextlib import contextmanager
from typing import Generator

T = TypeVar('T')
E = TypeVar('E')
U = TypeVar('U')

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
VALID_STYLES = tuple(sorted(["red", "green", "blue", "yellow", "cyan", "magenta", "white", "black"]))

# Validation functions
def is_valid_style(style: str) -> bool:
    """Check if a style string is valid for Rich."""
    return style in VALID_STYLES

def validate_style(style: str) -> ValidationResult:
    """Validate a style string."""
    return pipe(
        validate_input(style, "Style"),
        lambda s: Ok(s) if is_valid_style(s)
        else Error(DisplayError.Validation(f"Invalid style: {s}. Must be one of: {', '.join(VALID_STYLES)}"))
    )

def is_table_row(value: Any) -> TypeGuard[tuple[str, str]]:
    """Type guard for table row tuple."""
    return (
        isinstance(value, tuple) and 
        len(value) == 2 and 
        all(isinstance(x, str) for x in value)
    )

def validate_table_row(row: Any) -> TableRowResult:
    """Validate a table row."""
    return Ok(row) if is_table_row(row) else Error(DisplayError.Validation("Row must be a tuple of two strings"))

def validate_table_data(headers: list[str], rows: TableData) -> DisplayResult:
    """Validate table headers and rows."""
    if not headers:
        return Error(DisplayError.Validation("Headers list cannot be empty"))
    
    return pipe(
        headers,
        lambda h: Ok(h) if all(isinstance(h, str) for h in headers)
        else Error(DisplayError.Validation("Headers must be strings")),
        lambda _: Ok(rows) if all(len(row) == len(headers) for row in rows)
        else Error(DisplayError.Validation("All rows must have same length as headers")),
        lambda _: Ok(rows) if all(all(isinstance(cell, str) for cell in row) for row in rows)
        else Error(DisplayError.Validation("All cells must be strings")),
        lambda _: Ok(None)
    )

def validate_panel_inputs(title: str, content: str, style: str) -> Result[tuple[str, str, str], DisplayError]:
    """Validate panel creation inputs."""
    return pipe(
        validate_input(title, "Title"),
        lambda t: validate_input(content, "Content").map(lambda c: (t, c)),
        lambda tc: validate_style(style).map(lambda s: (tc[0], tc[1], s))
    )

def validate_progress_inputs[T](
    items: Iterable[T],
    process_fn: ProgressProcessor[T, U],
    description: str,
) -> Result[None, DisplayError]:
    """Validate progress display inputs."""
    try:
        items_list = list(items)
        return pipe(
            items_list,
            lambda i: Error(DisplayError.Validation("Items list cannot be empty")) if not i
            else Ok(i),
            lambda _: Error(DisplayError.Validation("Process function must be callable")) if not callable(process_fn)
            else Ok(None),
            lambda _: validate_input(description, "Description").map(lambda _: None)
        )
    except Exception as e:
        return Error(DisplayError.Validation(f"Invalid progress inputs: {str(e)}"))

console = Console()

def validate_input(value: str | None, name: str) -> ValidationResult:
    """Validates string input is not empty."""
    return Ok(value) if value else Error(DisplayError.Validation(f"{name} cannot be empty"))

async def display_message(message: Optional[str], style: Optional[str] = None) -> Result[None, DisplayError]:
    """Display a message with optional styling."""
    if message is None:
        return Error(DisplayError.Validation("Message cannot be None"))
    if not message:
        return Ok(None)
    try:
        if style:
            console.print(f"[{style}]{message}[/{style}]")
        else:
            console.print(message)
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display message", e))

async def success_message(message: str) -> Result[None, DisplayError]:
    """Display a success message."""
    return await display_message(message, "green")

async def error_message(message: str, details: Optional[str] = None) -> Result[None, DisplayError]:
    """Display an error message with optional details."""
    try:
        console.print(f"[red]{message}[/red]")
        if details:
            console.print(f"[red dim]Details: {details}[/red dim]")
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display error message", e))

async def warning_message(message: str) -> Result[None, DisplayError]:
    """Display a warning message."""
    return await display_message(message, "yellow")

def create_table_row(name_result: tuple[str, Result[str, T]]) -> TableRowResult:
    """Creates a single table row from a result."""
    name, result = name_result
    return pipe(
        validate_input(name, "Row name"),
        lambda n: Ok((n.title(), 
                   "[green]✨ Passed[/green]" if result.is_ok() 
                   else "[red]❌ Failed[/red]"))
    )

def add_row_to_table(table: Table, row: TableRow) -> TableResult:
    """Adds a row to the table in a functional way."""
    if not isinstance(table, Table):
        return Error(DisplayError.Validation("Invalid table object"))
    try:
        table.add_row(*row)
        return Ok(table)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to add row to table", e))

def _try_create_panel(content: str, title: str, style: str) -> PanelResult:
    try:
        return Ok(Panel(content, title=title, border_style=style))
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to create panel", e))

def create_panel(title: str, content: str, style: str) -> PanelResult:
    """Cria um painel com os parâmetros fornecidos."""
    return pipeline(
        # Inicia a pipeline com valor dummy
        lambda _: Ok(None),
        # Valida os inputs
        lambda _: validate_panel_inputs(title, content, style),
        # Tenta criar o painel de forma segura, capturando a exceção
        lambda _: _try_create_panel(content, title, style)
    )(None)

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

    return pipe(
        parts,
        lambda p: list(filter(None, p)),
        lambda filtered: Ok(separator.join(filtered)) if filtered
        else Error(DisplayError.Validation("At least one non-empty message part is required"))
    )

def create_multi_column_table(
    columns: list[tuple[str, Optional[str]]],
    rows: list[list[str]]
) -> Result[Table, DisplayError]:
    """Create a multi-column table."""
    try:
        if not columns:
            return Error(DisplayError.Validation("Headers list cannot be empty"))
        
        if not all(isinstance(col[0], str) for col in columns):
            return Error(DisplayError.Validation("Headers must be strings"))
        
        if not all(len(row) == len(columns) for row in rows):
            return Error(DisplayError.Rendering("Row length must match number of columns"))
        
        table = Table()
        for header, style in columns:
            table.add_column(header, style=style)
        
        for row in rows:
            table.add_row(*row)
        
        return Ok(table)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to create table", e))

async def display_table(table: Table) -> Result[None, DisplayError]:
    """Display a table."""
    try:
        console.print(table)
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display table", e))

async def confirm_action(message: str) -> Result[bool, DisplayError]:
    """Prompt for user confirmation."""
    try:
        return Ok(typer.confirm(message))
    except Exception as e:
        return Error(DisplayError.Interaction("Failed to get user confirmation", e))

async def display_rule(message: str, style: Optional[str] = None) -> Result[None, DisplayError]:
    """Display a horizontal rule with optional message."""
    try:
        rule = Rule(message, style=style)
        console.print(rule)
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display rule", e))

def batch_display_messages(messages: list[tuple[str, str]]) -> Result[None, DisplayError]:
    """Display multiple messages with different styles."""
    try:
        results = []
        for msg, style in messages:
            if not msg or not style:
                return Error(DisplayError.Validation("Message and style cannot be empty"))
            console.print(f"[{style}]{msg}[/{style}]")
            results.append(Ok(None))
        return Ok(None) if all(r.is_ok() for r in results) else Error(DisplayError.Rendering("Failed to display all messages"))
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display messages", e))

async def prompt_for_input(prompt: str, validator: callable) -> Result[str, DisplayError]:
    """Prompt for user input with validation."""
    try:
        value = typer.prompt(prompt)
        if validator(value):
            return Ok(value)
        return Error(DisplayError.Validation("Invalid input"))
    except Exception as e:
        return Error(DisplayError.Interaction("Failed to get user input", e))

async def display_indented_text(text: str, level: int = 1) -> Result[None, DisplayError]:
    """Display indented text."""
    try:
        indent = "  " * level
        console.print(f"{indent}{text}")
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display indented text", e))

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
                      lambda block: [create_panel(section[0], section[1], inner_style) for section in block],
                      lambda panels: Ok("\n".join(str(p.ok) for p in panels if p.is_ok())) if all(p.is_ok() for p in panels)
                      else Error(DisplayError.Validation("Failed to create inner panels")),
                      lambda content: content.bind(lambda c: create_panel(t, c, outer_style))
                  )))

async def display_progress[T, E](items: list[T], process: Callable[[T], Awaitable[Result[str, E]]], description: str) -> Result[None, DisplayError]:
    """Display a progress bar while processing items."""
    return pipe(
        validate_progress_inputs(items, process, description),
        lambda _: Try.create(lambda: Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn()
        )).map_error(lambda e: DisplayError.Rendering("Failed to create progress bar", e)),
        lambda progress: safe_display_with_progress(progress, items, process, description)
    )

async def safe_display_with_progress[T, E](
    progress: Progress, 
    items: list[T], 
    process: Callable[[T], Awaitable[Result[str, E]]], 
    description: str
) -> Result[None, DisplayError]:
    """Safely display progress with error aggregation."""
    try:
        with progress:
            task = progress.add_task(description, total=len(items))
            errors = []
            
            for item in items:
                result = await process(item)
                if result.is_error():
                    errors.append(result.unwrap_error())
                progress.advance(task)
            
            if errors:
                return Error(DisplayError.Execution("Some items failed to process", errors))
            return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display progress", e))

async def safe_display[T](display_fn: Callable[..., Awaitable[Result[T, DisplayError]]], *args, **kwargs) -> Result[T, DisplayError]:
    """Safely execute a display function with error handling."""
    try:
        return await display_fn(*args, **kwargs)
    except Exception as e:
        return Error(DisplayError.Rendering(f"Failed to execute {display_fn.__name__}", e))

@contextmanager
def ui_context_manager() -> Generator[None, None, None]:
    """Context manager para configuração e limpeza da UI."""
    try:
        console.clear()
        yield
    except Exception as e:
        error_message(f"UI error: {str(e)}")
    finally:
        console.clear()

async def handle_ui_error(error: DisplayError) -> Result[None, DisplayError]:
    """Trata erros da UI de forma funcional."""
    return pipe(
        await error_message(str(error), str(error.details) if hasattr(error, 'details') else None),
        lambda _: Error(error)
    )

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

async def with_retry[T](
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
                await warning_message(f"Operation failed, retrying in {delay} seconds...")
                await asyncio.sleep(delay)
    return result  # Return last error result

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

async def run_with_timeout(
    computation: Coroutine[Any, Any, Result[T, DisplayError]],
    timeout: float = 1.0,
) -> Result[T, DisplayError]:
    """Run a computation with a timeout.

    Args:
        computation: The computation to run.
        timeout: The timeout in seconds.

    Returns:
        The result of the computation, or an error if the computation timed out.
    """
    try:
        result = await asyncio.wait_for(computation, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        return Error(DisplayError(tag="timeout", timeout=(f"Operation timed out after {timeout} seconds", Exception("Timeout"))))
    except Exception as e:
        return Error(DisplayError(tag="execution", execution=("Operation failed", str(e))))
