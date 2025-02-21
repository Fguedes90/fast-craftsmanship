"""Error handling utilities."""
from collections.abc import Awaitable, Callable
from typing import TypeVar, Any, overload
import asyncio
import typer
from expression import effect

T = TypeVar('T')

@overload
def handle_command_errors(fn: Callable[..., T]) -> Callable[..., T]: ...

@overload
def handle_command_errors(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]: ...

def _handle_error(e: Exception) -> None:
    typer.echo(f"Error: {str(e)}")
    raise typer.Exit(1)

def handle_command_errors(fn: Callable[..., T] | Callable[..., Awaitable[T]]) -> Callable[..., T] | Callable[..., Awaitable[T]]:
    """Decorator to handle command errors gracefully using Expression's Try effect."""

    @effect.try_[T]()
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await fn(*args, **kwargs)
        except typer.Exit:
            raise
        except Exception as e:
            _handle_error(e)

    @effect.try_[T]()
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return fn(*args, **kwargs)
        except typer.Exit:
            raise
        except Exception as e:
            _handle_error(e)

    return async_wrapper if asyncio.iscoroutinefunction(fn) else sync_wrapper

def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None
) -> str:
    """Validate command operation and arguments using Expression's Try effect."""
    if operation not in valid_operations:
        valid_ops = ", ".join(valid_operations)
        raise typer.BadParameter(
            f"Invalid operation: {operation}. Valid operations: {valid_ops}"
        )

    if requires_name and operation in requires_name and not name:
        raise typer.BadParameter(
            f"Operation '{operation}' requires a name parameter"
        )

    return operation
