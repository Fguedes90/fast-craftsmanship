"""Error handling utilities following Railway-Oriented Programming pattern."""
from expression import Result, Ok, Error, pipe, effect
from collections.abc import Awaitable, Callable
from typing import TypeVar, Any, overload
import asyncio
import typer

T = TypeVar('T')

@overload
def handle_command_errors(fn: Callable[..., T]) -> Callable[..., T]: ...

@overload
def handle_command_errors(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]: ...

from fcship.utils.ui import display_message

class CommandError(Exception):
    """Erro específico para falhas em comandos."""
    pass

def _handle_error(e: Exception) -> Result[Any, CommandError]:
    """Convert exception to Result.Error and display error message."""
    error_msg = str(e)
    display_message(f"Error: {error_msg}", style="error")
    return Error(CommandError(error_msg))

def handle_command_errors(fn: Callable[..., T] | Callable[..., Awaitable[T]]) -> Callable[..., T] | Callable[..., Awaitable[T]]:
    """Decorator to handle command errors using Railway-Oriented Programming pattern.

    Converts exceptions to Result type and wraps side effects in the effect monad,
    using a fully functional style.
    """
    def handle_result(r: Result[T, Exception]) -> T:
        return r.match(lambda value: value, lambda error: _handle_and_exit(error))

    if asyncio.iscoroutinefunction(fn):
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            effect_result = await effect.from_async(fn)(*args, **kwargs).to_awaitable()
            return pipe(effect_result, handle_result)
        return wrapper
    else:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return pipe(effect.try_(fn)(*args, **kwargs), handle_result)
        return wrapper

def _handle_and_exit(error: Exception) -> None:
    """Handle error and exit with error code."""
    _ = _handle_error(error)
    raise typer.Exit(1)

def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None
) -> Result[str, Exception]:
    return (
        Ok(operation)
        .bind(lambda op: Ok(op) if op in valid_operations else Error(
            typer.BadParameter(f"Invalid operation: {op}. Valid operations: {', '.join(valid_operations)}")
        ))
        .bind(lambda op: Ok(op) if not (requires_name and op in requires_name and not name) else Error(
            typer.BadParameter(f"Operation '{op}' requires a name parameter")
        ))
    )
