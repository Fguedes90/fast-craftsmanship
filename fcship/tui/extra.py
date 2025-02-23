from collections.abc import Callable, Awaitable, Generator
import contextlib
import asyncio
from expression import Ok, Error, Result, pipe, effect, tagged_union
from rich.console import Console
from fcship.tui.errors import DisplayError
from typing import TypeVar, Dict, List, Optional, Any, Literal, Generic, Tuple
from dataclasses import dataclass

# Use the console instance from the tui display module.
from fcship.tui.display import console

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class UIOperation(Generic[T]):
    """Represents a UI operation with its context"""
    operation: Callable[[], Result[T, DisplayError]]
    setup: Optional[Callable[[], Result[None, DisplayError]]] = None
    cleanup: Optional[Callable[[], Result[None, DisplayError]]] = None

@dataclass(frozen=True)
class RetryConfig:
    """Configuration for retry operations"""
    max_attempts: int = 3
    delay: float = 1.0

@tagged_union
class UIError:
    """UI-related errors"""
    tag: Literal["validation", "rendering", "operation"]
    validation: str = None
    rendering: Tuple[str, Exception] = None
    operation: Tuple[str, Exception] = None

    @staticmethod
    def Validation(msg: str) -> "UIError":
        return UIError(tag="validation", validation=msg)

    @staticmethod
    def Rendering(msg: str, exc: Exception) -> "UIError":
        return UIError(tag="rendering", rendering=(msg, exc))

    @staticmethod
    def Operation(msg: str, exc: Exception) -> "UIError":
        return UIError(tag="operation", operation=(msg, exc))

async def safe_display(
    display_fn: Callable[..., Awaitable[Result[T, DisplayError]]],
    *args: Any,
    **kwargs: Any
) -> Result[T, DisplayError]:
    """Safely execute a display function with error handling"""
    return pipe(
        Ok((display_fn, args, kwargs)),
        lambda p: Ok(display_fn(*args, **kwargs)),
        lambda r: r.bind(lambda coro: Ok(asyncio.create_task(coro))),
        lambda t: t.bind(lambda task: Ok(asyncio.run(task)))
    ).map_error(lambda e: DisplayError.Rendering(f"Failed to execute {display_fn.__name__}", e))

@contextlib.contextmanager
def ui_context_manager() -> Generator[None, None, None]:
    """Context manager for UI setup and cleanup"""
    def safe_clear() -> Result[None, DisplayError]:
        return pipe(
            Ok(console.clear()),
            lambda _: Ok(None)
        ).map_error(lambda e: DisplayError.Rendering("Failed to clear console", e))
    
    result = safe_clear()
    if result.is_error():
        console.print(f"[red]UI error: {str(result.error)}[/red]")
    
    try:
        yield
    finally:
        safe_clear()

async def handle_ui_error(error: DisplayError) -> Result[None, DisplayError]:
    """Handle UI errors functionally"""
    return Error(error)

def with_fallback(
    operation: Callable[[], Result[T, DisplayError]],
    fallback: T,
    error_msg: Optional[str] = None
) -> T:
    """Execute a UI operation with fallback value on error"""
    return pipe(
        Ok(operation),
        lambda op: op.bind(lambda fn: fn()),
        lambda result: result.map_error(lambda e: (
            console.print(f"[red]{error_msg}: {str(e)}[/red]")
            if error_msg
            else None,
            fallback
        )[1]).unwrap_or(fallback)
    )

async def with_retry(
    operation: Callable[[], Result[T, DisplayError]],
    config: RetryConfig = RetryConfig()
) -> Result[T, DisplayError]:
    """Execute a UI operation with retry on failure"""
    async def try_operation(attempt: int) -> Result[T, DisplayError]:
        result = operation()
        if result.is_ok() or attempt >= config.max_attempts - 1:
            return result
        await asyncio.sleep(config.delay)
        return await try_operation(attempt + 1)
    
    return await try_operation(0)

def aggregate_errors(errors: List[DisplayError]) -> DisplayError:
    """Combine multiple errors into a single validation error"""
    return pipe(
        errors,
        lambda errs: map(str, errs),
        lambda msgs: "\n".join(msgs),
        lambda msg: DisplayError.Validation(msg)
    )

def recover_ui(
    operation: Callable[[], Result[T, DisplayError]],
    recovery_strategies: Dict[str, Callable[[], Result[T, DisplayError]]],
    config: RetryConfig = RetryConfig()
) -> Result[T, DisplayError]:
    """Execute a UI operation with specific recovery strategies"""
    def try_recover(attempt: int, last_error: Optional[DisplayError] = None) -> Result[T, DisplayError]:
        if attempt >= config.max_attempts:
            return Error(last_error or DisplayError.Validation("Unknown error"))
        
        result = operation()
        match result:
            case Ok(_):
                return result
            case Error(e) if hasattr(e, "tag") and e.tag in recovery_strategies:
                operation = recovery_strategies[e.tag]
                return try_recover(attempt + 1, e)
            case Error(e):
                return Error(e)
    
    return try_recover(0)

def with_ui_context(ui_op: UIOperation[T]) -> Result[T, DisplayError]:
    """Execute an operation in UI context with setup and cleanup"""
    def run_phase(phase: Optional[Callable[[], Result[None, DisplayError]]]) -> Result[None, DisplayError]:
        return phase() if phase else Ok(None)
    
    def handle_error(e: Exception) -> DisplayError:
        match e:
            case ValueError():
                return DisplayError.Validation(str(e))
            case IOError():
                return DisplayError.Rendering("IO operation failed", e)
            case TypeError():
                return DisplayError.Validation(str(e))
            case _:
                return DisplayError.Rendering("Operation failed", e)
    
    return pipe(
        run_phase(ui_op.setup),
        lambda setup: setup.bind(lambda _: ui_op.operation()),
        lambda result: result.bind(lambda r: pipe(
            run_phase(ui_op.cleanup),
            lambda cleanup: cleanup.map(lambda _: r)
        ))
    ).map_error(handle_error)
