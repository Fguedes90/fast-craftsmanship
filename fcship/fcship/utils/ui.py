"""UI utilities for CLI output."""
from rich.console import Console
from rich.panel import Panel
from expression import Result, Ok, effect, Try
import typer

console = Console()

@effect.try_[None]()
def display_message(message: str, style: str) -> None:
    """Display a message with given style using Expression's Try effect."""
    console.print(Panel(message, style=style))

def success_message(message: str) -> Result[None, Exception]:
    """Display a success message using Result type."""
    return Try.apply(lambda: display_message(message, "green"))

def error_message(message: str, details: str | None = None) -> Result[None, Exception]:
    """Display an error message with optional details using Result type."""
    full_message = f"{message}\n\n{details}" if details else message
    return Try.apply(lambda: display_message(full_message, "red"))

def format_message(parts: list[str], separator: str = "\n\n") -> Result[str, Exception]:
    """Format multiple message parts into a single message.

    Args:
        parts: List of message parts to combine
        separator: Separator to use between parts

    Returns:
        A Result containing the formatted message or an error
    """
    return Ok(separator.join(filter(None, parts)))

def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None
) -> Result[str, Exception]:
    """Valida a operação do comando e seus argumentos utilizando o tipo Result para tratamento de erro.

    Returns:
        Ok(operation) se a validação for bem-sucedida; caso contrário,
        retorna um Error com o typer.BadParameter adequado.
    """
    if operation not in valid_operations:
        valid_ops = ", ".join(valid_operations)
        return Result.error(typer.BadParameter(
            f"Invalid operation: {operation}. Valid operations: {valid_ops}"
        ))

    if requires_name and operation in requires_name and not name:
        return Result.error(typer.BadParameter(
            f"Operation '{operation}' requires a name parameter"
        ))
    return Ok(operation)
