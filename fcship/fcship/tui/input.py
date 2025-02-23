import typer
from expression import Ok, Error, Result
from fcship.tui.errors import DisplayError

async def prompt_for_input(prompt: str, validator: callable) -> Result[str, DisplayError]:
    try:
        value = typer.prompt(prompt)
        if validator(value):
            return Ok(value)
        return Error(DisplayError.Validation("Invalid input"))
    except Exception as e:
        return Error(DisplayError.Interaction("Failed to get user input", e))

async def confirm_action(message: str) -> Result[bool, DisplayError]:
    try:
        return Ok(typer.confirm(message))
    except Exception as e:
        return Error(DisplayError.Interaction("Failed to get user confirmation", e))
