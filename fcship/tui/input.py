from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

import typer

from expression import Error, Ok, Result, effect, pipe

from fcship.tui.errors import DisplayError

T = TypeVar("T")


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
def get_user_input(
    prompt: str, ctx: InputContext = input_ctx
) -> Generator[Result[str, DisplayError], Any, Result[str, DisplayError]]:
    """Get user input in a pure way"""
    try:
        value = ctx.input_handler.prompt(prompt)
        yield Ok(value)
    except Exception as e:
        yield Error(DisplayError.Input("Failed to get user input", str(e)))


def validate_input(value: str, validator: Validator) -> InputResult:
    """Validate user input"""
    return Ok(value) if validator(value) else Error(DisplayError.Validation("Invalid input"))


@effect.result[str, DisplayError]()
def prompt_for_input(
    prompt: str, validator: Validator, ctx: InputContext = input_ctx
) -> Generator[Result[str, DisplayError], Any, Result[str, DisplayError]]:
    """Get and validate user input"""
    result = yield from get_user_input(prompt, ctx)
    if result.is_error():
        yield result
    else:
        yield validate_input(result.ok, validator)


@effect.result[bool, DisplayError]()
def get_confirmation(
    message: str, ctx: InputContext = input_ctx
) -> Generator[Result[bool, DisplayError], Any, Result[bool, DisplayError]]:
    """Get user confirmation"""
    try:
        value = ctx.input_handler.confirm(message)
        yield Ok(value)
    except Exception as e:
        yield Error(DisplayError.Input("Failed to get user confirmation", str(e)))


@effect.result[bool, DisplayError]()
def confirm_action(message: str, ctx: InputContext = input_ctx) -> Result[bool, DisplayError]:
    """Get user confirmation for an action"""
    return pipe(
        get_confirmation(message, ctx),
        lambda result: result.bind(
            lambda confirmed: (
                Ok(True)
                if confirmed
                else Error(DisplayError.Validation("Action cancelled by user"))
            )
        ),
    )
