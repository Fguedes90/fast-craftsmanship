"""Validation utilities."""
from expression import Result, Ok, Error, pipe, Try, effect, option, Option
from collections.abc import Callable, Sequence
from typing import TypeVar
import typer
from .functional import option_to_result

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

@effect.try_[str]()
def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None
) -> Result[str, Exception]:
    """Validate command operation and arguments using Expression's Try effect."""
    valid_ops = ", ".join(valid_operations)
    return pipe(
        Ok(operation),
        lambda res: res.bind(lambda op: 
            Ok(op) if op in valid_operations else Error(
                typer.BadParameter(f"Invalid operation: {op}. Valid operations: {valid_ops}")
            )
        ),
        lambda res: res.bind(lambda op:
            Ok(op) if not (requires_name and op in requires_name and not name) else Error(
                typer.BadParameter(f"Operation '{op}' requires a name parameter")
            )
        )
    )

def validate(validator: Callable[[T], bool], error_msg: str) -> Callable[[T], Result[T, Exception]]:
    """Create a validation function that returns a Result."""
    return lambda value: Ok(value) if validator(value) else Error(ValueError(error_msg))

def compose_validations(*validators: Callable[[T], Result[T, Exception]]) -> Callable[[T], Result[T, Exception]]:
    """Compose multiple validation functions into a single validation."""
    from functools import reduce
    return lambda value: reduce(lambda acc, v: acc.bind(v), validators, Ok(value))


def validate_optional(value: Option[T], error_msg: str) -> Result[T, Exception]:
    """Validate an optional value, returning Error if Nothing."""
    return option_to_result(value, error_msg)
