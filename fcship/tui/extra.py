from collections.abc import Callable, Awaitable, Generator
import contextlib
import asyncio
from expression import Ok, Error, Result, pipe
from rich.console import Console
from fcship.fcship.utils.errors import DisplayError

# Use the console instance from the tui display module.
from fcship.tui.display import console

async def safe_display(display_fn: Callable[..., Awaitable[Result]], *args, **kwargs) -> Result:
    """
    Safely execute a display function with error handling.
    """
    try:
        return await display_fn(*args, **kwargs)
    except Exception as e:
        return Error(DisplayError.Rendering(f"Failed to execute {display_fn.__name__}", e))

@contextlib.contextmanager
def ui_context_manager() -> Generator[None, None, None]:
    """
    Context manager para configuração e limpeza da UI.
    """
    try:
        console.clear()
        yield
    except Exception as e:
        console.print(f"[red]UI error: {str(e)}[/red]")
    finally:
        console.clear()

async def handle_ui_error(error: DisplayError) -> Result:
    """
    Trata erros da UI de forma funcional.
    """
    # Here you might call an async error_message function if available.
    # For now, we simply return the error wrapped in an Error.
    return Error(error)

def with_fallback(operation: Callable[[], Result], fallback, error_msg: str | None = None):
    """
    Execute uma operação de UI com valor de fallback em caso de erro.
    """
    try:
        result = operation()
        if result.is_ok():
            return result.ok
        if error_msg:
            console.print(f"[red]{error_msg}[/red]")
        return fallback
    except Exception as e:
        if error_msg:
            console.print(f"[red]{error_msg}: {str(e)}[/red]")
        return fallback

async def with_retry(operation: Callable[[], Result], max_attempts: int = 3, delay: float = 1.0) -> Result:
    """
    Execute uma operação de UI com tentativas de repetição em caso de falha.
    """
    for attempt in range(max_attempts):
        result = operation()
        if result.is_ok():
            return result
        if attempt < max_attempts - 1:
            try:
                await asyncio.sleep(delay)
            except Exception:
                pass
    return result

def aggregate_errors(errors: list[DisplayError]) -> DisplayError:
    """
    Combina múltiplos erros em um único erro de validação.
    """
    error_messages = []
    for error in errors:
        error_messages.append(str(error))
    return DisplayError.Validation("\n".join(error_messages))

def recover_ui(operation: Callable[[], Result], recovery_strategies: dict[str, Callable[[], Result]], max_attempts: int = 3) -> Result:
    """
    Executa uma operação de UI com estratégias de recuperação específicas.
    """
    attempt = 0
    last_error = None
    while attempt < max_attempts:
        result = operation()
        if result.is_ok():
            return result
        last_error = result.error
        if hasattr(last_error, "tag") and last_error.tag in recovery_strategies:
            attempt += 1
            operation = recovery_strategies[last_error.tag]
        else:
            break
    return Error(last_error or DisplayError.Validation("Unknown error"))

def with_ui_context(operation: Callable[[], Result], setup: Callable[[], Result] | None = None, cleanup: Callable[[], Result] | None = None) -> Result:
    """
    Executa uma operação no contexto de UI com funções de setup e cleanup.
    """
    try:
        if setup:
            setup_result = setup()
            if setup_result.is_error():
                return Error(setup_result.error)
        result = operation()
        if cleanup:
            cleanup_result = cleanup()
            if cleanup_result.is_error():
                return Error(cleanup_result.error)
        return result
    except ValueError as e:
        return Error(DisplayError.Validation(str(e)))
    except IOError as e:
        return Error(DisplayError.Rendering("IO operation failed", e))
    except TypeError as e:
        return Error(DisplayError.Validation(str(e)))
    except RuntimeError as e:
        return Error(DisplayError.Rendering("Operation failed", e))
