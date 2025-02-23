import asyncio
from typing import TypeVar, Callable, List, Coroutine, Any, Generic, Awaitable
from expression import Ok, Error, Result, pipe, Try, effect
from expression.collections import seq
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from fcship.tui.errors import DisplayError
from fcship.tui.helpers import validate_progress_inputs
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class ProgressConfig:
    """Configuration for progress display"""
    description: str
    total: int
    columns: List[Any]

def create_progress_config(description: str, total: int) -> ProgressConfig:
    """Create a progress configuration with default columns"""
    return ProgressConfig(
        description=description,
        total=total,
        columns=[
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn()
        ]
    )

def create_progress(config: ProgressConfig) -> Result[Progress, DisplayError]:
    """Create a progress bar with the given configuration"""
    return Try.create(
        lambda: Progress(*config.columns)
    ).map_error(
        lambda e: DisplayError.Rendering("Failed to create progress bar", e)
    )

async def process_item(process: Callable[[T], Awaitable[Result[Any, E]]], item: T) -> Result[None, E]:
    """Process a single item and return its result"""
    return await process(item)

async def process_items(
    progress: Progress,
    task_id: int,
    items: List[T],
    process: Callable[[T], Awaitable[Result[Any, E]]]
) -> Result[None, List[E]]:
    """Process all items and collect errors"""
    async def process_and_advance(item: T) -> Result[None, E]:
        result = await process_item(process, item)
        progress.advance(task_id)
        return result

    results = await asyncio.gather(*[process_and_advance(item) for item in items])
    errors = [r.unwrap_error() for r in results if r.is_error()]
    
    return (
        Ok(None)
        if not errors
        else Error(errors)
    )

async def safe_display_with_progress(
    progress: Progress,
    items: List[T],
    process: Callable[[T], Awaitable[Result[Any, E]]],
    description: str
) -> Result[None, DisplayError]:
    """Safely display progress while processing items"""
    def handle_errors(errors: List[E]) -> Result[None, DisplayError]:
        return Error(DisplayError.Execution("Some items failed to process", errors))

    with progress:
        task_id = progress.add_task(description, total=len(items))
        result = await process_items(progress, task_id, items, process)
        return (
            Ok(None)
            if result.is_ok()
            else handle_errors(result.unwrap_error())
        )

async def display_progress(
    items: List[T],
    process: Callable[[T], Awaitable[Result[Any, E]]],
    description: str
) -> Result[None, DisplayError]:
    """Display progress while processing items"""
    # Validate inputs
    validation = validate_progress_inputs(items, process, description)
    if validation.is_error():
        return validation
    
    # Create progress configuration and progress bar
    config = create_progress_config(description, len(items))
    progress = create_progress(config)
    if progress.is_error():
        return progress
    
    # Process items with progress display
    return await safe_display_with_progress(progress.unwrap(), items, process, description)

async def run_with_timeout(
    computation: Coroutine[Any, Any, Result[T, E]],
    timeout: float = 1.0
) -> Result[T, DisplayError]:
    """Run a computation with a timeout"""
    try:
        result = await asyncio.wait_for(computation, timeout=timeout)
        return result.map_error(lambda e: DisplayError.Execution("Operation failed", str(e)))
    except asyncio.TimeoutError:
        return Error(DisplayError.Timeout(f"Operation timed out after {timeout} seconds", Exception("Timeout")))
    except Exception as e:
        return Error(DisplayError.Execution("Operation failed", str(e)))
