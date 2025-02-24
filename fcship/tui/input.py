import typer
from collections.abc import Generator
from expression import Ok, Error, Result, effect, pipe
from fcship.tui.errors import DisplayError
from typing import Callable, TypeVar, Protocol, Any, ForwardRef
from dataclasses import dataclass

T = TypeVar('T')

# Protocol for input handling
class InputProtocol(Protocol):
    def prompt(self, text: str) -> str: ...
    def confirm(self, text: str) -> bool: ...

@dataclass(frozen=True)
class InputContext:
    input_handler: InputProtocol

class TyperInputHandler:
    def prompt(self, text: str) -> str:
        return typer.prompt(text)
    
    def confirm(self, text: str) -> bool:
        return typer.confirm(text)

# Type aliases for improved readability
InputResult = Result[str, DisplayError]
BoolResult = Result[bool, DisplayError]
Validator = Callable[[str], bool]

# Create input context
input_ctx = InputContext(input_handler=TyperInputHandler())

@effect.result[str, DisplayError]()
def get_user_input(ctx: InputContext, prompt: str) -> Generator[Result[str, DisplayError], Any, Result[str, DisplayError]]:
    """Get user input in a pure way"""
    try:
        value = ctx.input_handler.prompt(prompt)
        yield Ok(value)
    except Exception as e:
        yield Error(DisplayError.Interaction("Failed to get user input", e))

def validate_input(value: str, validator: Validator) -> InputResult:
    """Validate user input"""
    return (
        Ok(value)
        if validator(value)
        else Error(DisplayError.Validation("Invalid input"))
    )

@effect.result[str, DisplayError]()
def prompt_for_input(ctx: InputContext, prompt: str, validator: Validator) -> Generator[Result[str, DisplayError], Any, Result[str, DisplayError]]:
    """Prompt for and validate user input"""
    result = yield from get_user_input(ctx, prompt)
    if result.is_error():
        return result
    return validate_input(result.ok, validator)

@effect.result[bool, DisplayError]()
def get_confirmation(ctx: InputContext, message: str) -> Generator[Result[bool, DisplayError], Any, Result[bool, DisplayError]]:
    """Get user confirmation in a pure way"""
    try:
        value = ctx.input_handler.confirm(message)
        yield Ok(value)
    except Exception as e:
        yield Error(DisplayError.Interaction("Failed to get user confirmation", e))

@effect.result[bool, DisplayError]()
def confirm_action(ctx: InputContext, message: str) -> Result[bool, DisplayError]:
    """Get user confirmation with error handling"""
    value = yield from get_confirmation(ctx, message)
    match value:
        case Ok(value):
            return Ok(value)
        case Error(e):
            return Error(e)
