import asyncio
import typer
from expression import Ok, Error, Result
from fcship.tui.helpers import validate_input
from fcship.tui.errors import DisplayError
from rich.console import Console
from rich.rule import Rule

console = Console()

async def display_message(message: str | None, style: str | None = None) -> Result[None, DisplayError]:
    if message is None:
        return Error(DisplayError.Validation("Message cannot be None"))
    if not message:
        return Ok(None)
    try:
        if style:
            console.print(f"[{style}]{message}[/{style}]")
        else:
            console.print(message)
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display message", e))

async def success_message(message: str) -> Result[None, DisplayError]:
    return await display_message(message, "green")

async def error_message(message: str, details: str | None = None) -> Result[None, DisplayError]:
    try:
        console.print(f"[red]{message}[/red]")
        if details:
            console.print(f"[red dim]Details: {details}[/red dim]")
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display error message", e))

async def warning_message(message: str) -> Result[None, DisplayError]:
    return await display_message(message, "yellow")

def display_rule(message: str, style: str | None = None) -> Result[None, DisplayError]:
    try:
        rule = Rule(message, style=style)
        console.print(rule)
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display rule", e))

async def batch_display_messages(messages: list[tuple[str, str]]) -> Result[None, DisplayError]:
    try:
        results = []
        for msg, style in messages:
            if not msg or not style:
                return Error(DisplayError.Validation("Message and style cannot be empty"))
            console.print(f"[{style}]{msg}[/{style}]")
            results.append(Ok(None))
        return Ok(None) if all(r.is_ok() for r in results) else Error(DisplayError.Rendering("Failed to display all messages"))
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display messages", e))

async def display_indented_text(text: str, level: int = 1) -> Result[None, DisplayError]:
    try:
        indent = "  " * level
        console.print(f"{indent}{text}")
        return Ok(None)
    except Exception as e:
        return Error(DisplayError.Rendering("Failed to display indented text", e))
