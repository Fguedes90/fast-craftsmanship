"""UI utilities for CLI output."""
from rich.console import Console
from rich.panel import Panel
from expression import Result, Ok, Error, effect, Try
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
        return Error(typer.BadParameter(
            f"Invalid operation: {operation}. Valid operations: {valid_ops}"
        ))

    if requires_name and operation in requires_name and not name:
        return Error(typer.BadParameter(
            f"Operation '{operation}' requires a name parameter"
        ))
    return Ok(operation)

def warning_message(message: str) -> Result[None, Exception]:
    """Display a warning message using Result type with yellow style."""
    return Try.apply(lambda: display_message(message, "yellow"))

def display_table(headers: list[str], rows: list[list[str]], title: str | None = None) -> Result[None, Exception]:
    """Display a table using Rich for formatting.
    
    Args:
        headers: List of table headers.
        rows: List of table rows, each row is a list of strings.
        title: Optional title for the table.
    
    Returns:
        A Result with None if successful, or an error.
    """
    from rich.table import Table
    def _display() -> None:
        table = Table(title=title) if title else Table()
        list(map(lambda h: table.add_column(h), headers))
        list(map(lambda row: table.add_row(*row), rows))
        console.print(table)
    return Try.apply(_display)

def confirm_action(prompt: str) -> Result[bool, Exception]:
    """Display a confirmation prompt and return the boolean result as a Result.
    
    Args:
        prompt: The message to display for confirmation.
    
    Returns:
        Ok(True/False) if the confirmation is successful, or an Error if an exception occurs.
    """
    return Try.apply(lambda: typer.confirm(prompt))
    
def display_rule(message: str, style: str = "blue") -> Result[None, Exception]:
    """Display a horizontal rule with a centered message using Rich's console.rule.
    
    Args:
        message: The text to display in the rule.
        style: The style to apply to the rule (default: "blue").
    
    Returns:
        A Result with None if the rule is displayed successfully, or an error.
    """
    return Try.apply(lambda: console.rule(message, style=style))
