"""Error handling utilities following Railway-Oriented Programming pattern."""
from expression import Result, Ok, Error, pipe, effect
from collections.abc import Awaitable, Callable
from typing import TypeVar, Any, overload
import asyncio
import typer
from fcship.tui import error_message, DisplayContext
from fcship.tui.display import console

T = TypeVar('T')
SyncFn = Callable[..., T]
AsyncFn = Callable[..., Awaitable[T]]
Fn = SyncFn | AsyncFn

@overload
def handle_command_errors(fn: SyncFn) -> SyncFn: ...

@overload
def handle_command_errors(fn: AsyncFn) -> AsyncFn: ...

class CommandError(Exception):
    """Erro específico para falhas em comandos."""
    pass

def _on_error(e: Exception) -> None:
    try:
        disp = error_message.__wrapped__
    except AttributeError:
        disp = error_message
    ctx = DisplayContext(console=console)
    disp(ctx, str(e))
    raise typer.Exit(1)

def handle_command_errors(fn: Fn) -> Fn:
    def handle_result(r: Result[T, Exception]) -> T:
        return r.ok if r.is_ok() else _on_error(r.error)

    if asyncio.iscoroutinefunction(fn):
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                result = await fn(*args, **kwargs)
                return handle_result(Ok(result))
            except Exception as e:
                return handle_result(Error(e))
        return wrapper  # type: ignore
    else:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                result = fn(*args, **kwargs)
                return handle_result(Ok(result))
            except Exception as e:
                return handle_result(Error(e))
        return wrapper

def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None
) -> str:
    res = pipe(
        Ok(operation),
        lambda res: res.bind(
            lambda op: (
                Ok(op)
                if op in valid_operations
                else Error(
                    typer.BadParameter(
                        f"Invalid operation: {op}. Valid operations: {', '.join(valid_operations)}"
                    )
                )
            )
        ),
        lambda res: res.bind(
            lambda op: (
                Ok(op)
                if not requires_name or op not in requires_name or name
                else Error(
                    typer.BadParameter(
                        f"Operation '{op}' requires a name parameter"
                    )
                )
            )
        ),
    )
    if res.is_ok():
        return res.ok
    else:
        raise res.error
