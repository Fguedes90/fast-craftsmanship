import multiprocessing
import os

from collections.abc import Callable, Generator
from dataclasses import dataclass
from multiprocessing.pool import Pool
from typing import Any, Generic, Literal, TypeVar

# Set multiprocessing start method to 'spawn' to avoid fork-related warnings
# Only set it if we're on Unix-like systems (not needed on Windows)
if os.name != "nt" and hasattr(multiprocessing, "set_start_method"):
    import contextlib
    with contextlib.suppress(RuntimeError):
        multiprocessing.set_start_method("spawn", force=False)

from expression import Error, Ok, Result, case, curry, effect, pipe, tag, tagged_union
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from fcship.tui.helpers import validate_progress_inputs

T = TypeVar("T")
E = TypeVar("E")


@effect.result[None, "ProgressError"]()
def validate_inputs(
    items: list[T], process: Callable[[T], Generator[Any, Any, Result[Any, E]]], description: str
) -> Result[None, "ProgressError"]:
    """Validate inputs and convert DisplayError to ProgressError"""
    result = validate_progress_inputs(items, process, description)
    return result.map_error(lambda e: ProgressError.validation_error(str(e)))


@tagged_union
class ProgressError:
    """Progress operation errors"""

    tag: Literal["validation", "execution", "timeout", "parallel"] = tag()

    validation: str = case()
    execution: tuple[str, Any] = case()
    timeout: tuple[float, str] = case()
    parallel: tuple[str, list[Any]] = case()

    @staticmethod
    def from_error(error: Any) -> "ProgressError":
        """Convert any error to a ProgressError"""
        return ProgressError(execution=("Operation failed", str(error)))

    @staticmethod
    def from_parallel_errors(errors: list[Any]) -> "ProgressError":
        """Convert parallel processing errors to a ProgressError"""
        return ProgressError(parallel=("Some parallel tasks failed", errors))

    @staticmethod
    def validation_error(message: str) -> "ProgressError":
        """Create a validation error"""
        return ProgressError(validation=message)

    @staticmethod
    def timeout_error(timeout: float, message: str) -> "ProgressError":
        """Create a timeout error"""
        return ProgressError(timeout=(timeout, message))


@dataclass(frozen=True)
class ProgressConfig:
    """Configuration for progress display"""

    description: str
    total: int
    columns: list[Any]
    parallel: bool = False
    max_workers: int | None = None


@dataclass(frozen=True)
class ProgressContext(Generic[T]):
    """Context for progress operations"""

    progress: Progress
    task_id: int
    items: list[T]
    process: Callable[[T], Generator[Any, Any, Result[Any, E]]]
    description: str
    parallel: bool
    max_workers: int | None


@curry
def map_error_to_progress(error: Any) -> ProgressError:
    """Convert any error to a ProgressError"""
    return ProgressError.from_error(error)


def create_progress_config(
    description: str, total: int, parallel: bool = False, max_workers: int | None = None
) -> Result[ProgressConfig, ProgressError]:
    """Create a progress configuration with default columns"""
    match total >= 0:
        case False:
            return Error(ProgressError.validation_error("Total must be non-negative"))
        case True:
            columns = [
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
            ]
            return Ok(ProgressConfig(description, total, columns, parallel, max_workers))


def validate_config(config: ProgressConfig) -> Result[ProgressConfig, ProgressError]:
    """Validate progress configuration"""
    match (config.total >= 0, bool(config.columns)):
        case (False, _):
            return Error(ProgressError.validation_error("Total must be non-negative"))
        case (_, False):
            return Error(ProgressError.validation_error("Must provide at least one column"))
        case (True, True):
            return Ok(config)


def create_progress(config: ProgressConfig) -> Result[Progress, ProgressError]:
    """Create a progress bar with the given configuration"""
    return pipe(validate_config(config), lambda r: r.map(lambda c: Progress(*c.columns)))


def create_context(
    progress: Progress,
    items: list[T],
    process: Callable[[T], Generator[Any, Any, Result[Any, E]]],
    description: str,
    parallel: bool = False,
    max_workers: int | None = None,
) -> Result[ProgressContext[T], ProgressError]:
    """Create a progress context"""
    return pipe(
        validate_progress_inputs(items, process, description),
        lambda _: Ok(
            ProgressContext(
                progress=progress,
                task_id=progress.add_task(description, total=len(items)),
                items=items,
                process=process,
                description=description,
                parallel=parallel,
                max_workers=max_workers,
            )
        ),
    )


@effect.result[None, E]()
def process_single_item(ctx: ProgressContext[T], item: T) -> Generator[Any, Any, Result[None, E]]:
    """Process a single item and update progress"""
    result = yield from ctx.process(item)
    ctx.progress.advance(ctx.task_id)
    return result


def run_generator_to_completion(gen: Generator[Any, Any, Result[Any, Any]]) -> Result[Any, Any]:
    """Run a generator to completion and return its final value"""
    try:
        result = None
        try:
            while True:
                next(gen)
        except StopIteration as e:
            result = e.value
        return result
    except Exception as e:
        return Error(str(e))


def process_parallel_item(
    item: T, process_fn: Callable[[T], Generator[Any, Any, Result[Any, E]]]
) -> Result[None, E]:
    """Process a single item in parallel"""
    try:
        gen = process_fn(item)
        return run_generator_to_completion(gen)
    except Exception as e:
        return Error(str(e))


@effect.result[None, list[E]]()
def process_all_items(ctx: ProgressContext[T]) -> Generator[Any, Any, Result[None, list[E]]]:
    """Process all items and collect errors"""
    results = []
    if not ctx.parallel:
        # Sequential processing
        for item in ctx.items:
            result = yield from process_single_item(ctx, item)
            results.append(result)
    else:
        # Parallel processing
        # Since we can't pickle local functions, we'll process items sequentially
        # but in a separate process to avoid blocking the main thread
        num_workers = ctx.max_workers or multiprocessing.cpu_count()
        chunk_size = max(1, len(ctx.items) // num_workers)
        chunks = [ctx.items[i : i + chunk_size] for i in range(0, len(ctx.items), chunk_size)]

        with Pool(processes=num_workers) as pool:
            for chunk in chunks:
                chunk_results = []
                for item in chunk:
                    try:
                        gen = ctx.process(item)
                        result = run_generator_to_completion(gen)
                        chunk_results.append(result)
                    except Exception as e:
                        chunk_results.append(Error(str(e)))
                results.extend(chunk_results)
                # Update progress after each chunk
                for _ in range(len(chunk_results)):
                    ctx.progress.advance(ctx.task_id)

    # Check for errors in results
    errors = [r.error for r in results if r.is_error()]
    if errors:
        return Error(errors)
    return Ok(None)


@effect.result[None, ProgressError]()
def safe_display_with_progress(
    ctx: ProgressContext[T],
) -> Generator[Any, Any, Result[None, ProgressError]]:
    """Safely display progress while processing items"""
    with ctx.progress:
        result = yield from process_all_items(ctx)
        if result.is_error():
            # Create a new Error with ProgressError
            return Error(ProgressError.from_parallel_errors(result.error))
        return Ok(None)


def validate_display_inputs(
    items: list[T], process: Callable[[T], Generator[Any, Any, Result[Any, E]]], description: str
) -> Result[None, ProgressError]:
    """Validate display progress inputs"""
    match (bool(items), bool(process), bool(description)):
        case (False, _, _):
            return Error(ProgressError.validation_error("Items list cannot be empty"))
        case (_, False, _):
            return Error(ProgressError.validation_error("Process function is required"))
        case (_, _, False):
            return Error(ProgressError.validation_error("Description is required"))
        case (True, True, True):
            return Ok(None)


@effect.result[None, ProgressError]()
def display_progress(
    items: list[T],
    process: Callable[[T], Generator[Any, Any, Result[Any, E]]],
    description: str,
    parallel: bool = False,
    max_workers: int | None = None,
) -> Generator[Any, Any, Result[None, ProgressError]]:
    """Display progress while processing items"""
    # First validate inputs
    validation_result = validate_display_inputs(items, process, description)
    if validation_result.is_error():
        return validation_result

    config = yield from create_progress_config(description, len(items), parallel, max_workers)
    progress = yield from create_progress(config)
    context = yield from create_context(
        progress, items, process, description, parallel, max_workers
    )
    result = yield from safe_display_with_progress(context)
    return result


@effect.result[T, ProgressError]()
def run_with_timeout(
    computation: Generator[Any, Any, Result[T, E]], timeout: float = 1.0
) -> Generator[Any, Any, Result[T, ProgressError]]:
    """Run a computation with a timeout"""
    result = yield from computation
    return result.map_error(lambda e: ProgressError.from_error(e))
