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

    Converts exceptions to Result type and wraps side effects in effect monad.
    Following the functional programming guidelines for error handling.
    """
    if asyncio.iscoroutinefunction(fn):
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            # Convert async function to effect and handle errors
            effect_result = await effect.from_async(fn)(*args, **kwargs).to_awaitable()
            return pipe(
                effect_result,
                lambda r: r.match(
                    lambda value: value,
                    lambda error: _handle_and_exit(error)
                )
            )
        return wrapper
    else:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Convert sync function to effect and handle errors
            return pipe(
                effect.try_(fn)(*args, **kwargs),
                lambda r: r.match(
                    lambda value: value,
                    lambda error: _handle_and_exit(error)
                )
            )
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
    """Validate command operation and arguments using Railway-Oriented Programming pattern."""
    if operation not in valid_operations:
        valid_ops = ", ".join(valid_operations)
        return Error(typer.BadParameter(
            f"Invalid operation: {operation}. Valid operations: {valid_ops}"
        ))
    if requires_name and operation in requires_name and not name:
        return Error(typer.BadParameter(
            f"Operation '{operation}' requires a name parameter"
        ))
    return Ok(operation)
