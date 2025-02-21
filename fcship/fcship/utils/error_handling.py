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

def handle_command_errors(fn: Callable[..., T] | Callable[..., Awaitable[T]]) -> Callable[..., T] | Callable[..., Awaitable[T]]:
    """Decorator to handle command errors gracefully using Expression's Try effect."""
    
    @effect.try_[T]()
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return await fn(*args, **kwargs)
        except typer.Exit:
            raise
        except Exception as e:
            typer.echo(f"Error: {str(e)}")
            raise typer.Exit(1)

    @effect.try_[T]()
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return fn(*args, **kwargs)
        except typer.Exit:
            raise
        except Exception as e:
            typer.echo(f"Error: {str(e)}")
            raise typer.Exit(1)

    return async_wrapper if asyncio.iscoroutinefunction(fn) else sync_wrapper