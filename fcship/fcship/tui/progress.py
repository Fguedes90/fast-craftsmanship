import asyncio
from typing import Coroutine
from expression import Ok, Error, Result, pipe, Try
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from fcship.tui.errors import DisplayError
from fcship.tui.helpers import validate_progress_inputs

async def display_progress(items: list, process: callable, description: str) -> Result[None, DisplayError]:
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

async def safe_display_with_progress(progress: Progress, items: list, process: callable, description: str) -> Result[None, DisplayError]:
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

async def run_with_timeout(computation: Coroutine, timeout: float = 1.0) -> Result:
    try:
        return await asyncio.wait_for(computation, timeout=timeout)
    except asyncio.TimeoutError:
        return Error(DisplayError.Timeout(f"Operation timed out after {timeout} seconds", Exception("Timeout")))
    except Exception as e:
        return Error(DisplayError.Execution("Operation failed", str(e)))
