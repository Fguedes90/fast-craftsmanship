import asyncio
import contextlib

from collections.abc import Awaitable, Callable, Generator
from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar

from expression import Error, Ok, Result, pipe, tagged_union

# Use the console instance from the tui display module.
from fcship.tui.display import console
from fcship.tui.errors import DisplayError

from .types import DisplayError, console

T = TypeVar("T")
E = TypeVar("E")

# Type aliases
UIOperation = Callable[[], Result[T, DisplayError]]
AsyncUIOperation = Callable[[], Awaitable[Result[T, DisplayError]]]


@dataclass(frozen=True)
class UIOperation(Generic[T]):
    """Represents a UI operation with its context"""

    operation: Callable[[], Result[T, DisplayError]]
    setup: Callable[[], Result[None, DisplayError]] | None = None
    cleanup: Callable[[], Result[None, DisplayError]] | None = None


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
    rendering: tuple[str, Exception] = None
    operation: tuple[str, Exception] = None

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
    display_fn: Callable[..., Awaitable[Result[T, DisplayError]]], *args: Any, **kwargs: Any
) -> Result[T, DisplayError]:
    """Safely execute a display function with error handling"""
    return pipe(
        Ok((display_fn, args, kwargs)),
        lambda p: Ok(display_fn(*args, **kwargs)),
        lambda r: r.bind(lambda coro: Ok(asyncio.create_task(coro))),
        lambda t: t.bind(lambda task: Ok(asyncio.run(task))),
    ).map_error(lambda e: DisplayError.Rendering(f"Failed to execute {display_fn.__name__}", e))


@contextlib.contextmanager
def ui_context_manager() -> Generator[None, None, None]:
    """Context manager for UI setup and cleanup"""

    def safe_clear() -> Result[None, DisplayError]:
        return pipe(Ok(console.clear()), lambda _: Ok(None)).map_error(
            lambda e: DisplayError.Rendering("Failed to clear console", e)
        )

    result = safe_clear()
    if result.is_error():
        console.print(f"[red]UI error: {result.error!s}[/red]")

    try:
        yield
    finally:
        safe_clear()


def handle_ui_error(error: Exception) -> Result[None, UIError]:
    """Handle UI-related errors and convert them to UIError"""
    match error:
        case ValueError():
            return Error(UIError.Validation(str(error)))
        case IOError():
            return Error(UIError.Rendering("IO operation failed", error))
        case _:
            return Error(UIError.Operation("Operation failed", error))


def with_fallback(
    operation: Callable[[], Result[T, DisplayError]], fallback: T, error_msg: str | None = None
) -> T:
    """Execute a UI operation with fallback value on error"""
    result = operation()
    if result.is_ok():
        return result.ok
    if error_msg:
        console.print(f"[red]{error_msg}: {result.error!s}[/red]")
    return fallback


async def with_retry(
    operation: Callable[[], Result[T, DisplayError]], config: RetryConfig = RetryConfig()
) -> Result[T, DisplayError]:
    """Execute a UI operation with retry on failure"""

    async def try_operation(attempt: int) -> Result[T, DisplayError]:
        result = operation()
        if result.is_ok() or attempt >= config.max_attempts - 1:
            return result
        await asyncio.sleep(config.delay)
        return await try_operation(attempt + 1)

    return await try_operation(0)


def aggregate_errors(errors: list[DisplayError]) -> DisplayError:
    """Combine multiple errors into a single validation error"""
    return pipe(
        errors,
        lambda errs: map(str, errs),
        lambda msgs: "\n".join(msgs),
        lambda msg: DisplayError.Validation(msg),
    )


def recover_ui(
    operation: Callable[[], Result[T, DisplayError]],
    recovery_strategies: dict[str, Callable[[], Result[T, DisplayError]]],
    config: RetryConfig = RetryConfig(),
) -> Result[T, DisplayError]:
    """Execute a UI operation with specific recovery strategies"""

    def try_recover(
        attempt: int, last_error: DisplayError | None = None
    ) -> Result[T, DisplayError]:
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


def with_ui_context(
    operation: Callable[[], T] | UIOperation[T],
    setup: Callable[[], None] | None = None,
    cleanup: Callable[[], None] | None = None,
) -> Result[T, DisplayError]:
    """Execute an operation in UI context with setup and cleanup"""

    def wrap_operation(fn: Callable[[], T]) -> Callable[[], Result[T, DisplayError]]:
        def wrapped() -> Result[T, DisplayError]:
            try:
                result = fn()
                return Ok(result)
            except Exception as e:
                return Error(handle_error(e))

        return wrapped

    def run_phase(phase: Callable[[], None] | None) -> Result[None, DisplayError]:
        if not phase:
            return Ok(None)
        try:
            phase()
            return Ok(None)
        except Exception as e:
            return Error(handle_error(e))

    def handle_error(e: Exception) -> DisplayError:
        match e:
            case ValueError():
                return DisplayError.Rendering("Operation failed", e)
            case IOError():
                return DisplayError.Rendering("IO operation failed", e)
            case TypeError():
                return DisplayError.Validation(str(e))
            case _:
                return DisplayError.Rendering("Operation failed", e)

    # Convert operation to UIOperation if it's a plain function
    ui_op = (
        operation
        if isinstance(operation, UIOperation)
        else UIOperation(operation=wrap_operation(operation), setup=setup, cleanup=cleanup)
    )

    # Run the operation in context
    return pipe(
        run_phase(ui_op.setup),
        lambda setup_result: setup_result.bind(
            lambda _: (
                ui_op.operation() if isinstance(ui_op, UIOperation) else wrap_operation(ui_op)()
            )
        ),
        lambda result: result.bind(
            lambda r: pipe(
                run_phase(ui_op.cleanup), lambda cleanup_result: cleanup_result.map(lambda _: r)
            )
        ),
    )
