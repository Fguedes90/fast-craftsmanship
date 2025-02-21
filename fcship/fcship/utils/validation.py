"""Validation utilities."""
from collections.abc import Callable, Sequence
from typing import TypeVar
import typer
from expression import Result, Ok, Error, pipe, Try, effect, option, Option

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

@effect.try_[str]()
def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None
) -> str:
    """Validate command operation and arguments using Expression's Try effect."""
    if operation not in valid_operations:
        valid_ops = ", ".join(valid_operations)
        raise typer.BadParameter(
            f"Invalid operation: {operation}. Valid operations: {valid_ops}"
        )
        
    if requires_name and operation in requires_name and not name:
        raise typer.BadParameter(
            f"Operation '{operation}' requires a name parameter"
        )
    
    return operation

def validate(validator: Callable[[T], bool], error_msg: str) -> Callable[[T], Result[T, Exception]]:
    """Create a validation function that returns a Result."""
    return lambda value: Ok(value) if validator(value) else Error(ValueError(error_msg))

def compose_validations(*validators: Callable[[T], Result[T, Exception]]) -> Callable[[T], Result[T, Exception]]:
    """Compose multiple validation functions into a single validation."""
    def composed(value: T) -> Result[T, Exception]:
        result = Ok(value)
        for v in validators:
            result = result.bind(v)
            if result.is_error():
                break
        return result
    return composed

def sequence_validations(validations: Sequence[Result[T, E]]) -> Result[Sequence[T], E]:
    """Convert a sequence of validation Results into a Result of sequence.
    
    This is useful when you want to collect all validation results and only proceed
    if all validations pass.
    """
    def folder(acc: Result[list[T], E], item: Result[T, E]) -> Result[list[T], E]:
        return pipe(
            acc,
            lambda xs: pipe(
                item,
                lambda x: Ok([*xs, x]) if acc.is_ok() else acc
            )
        )
    
    return pipe(
        validations,
        lambda xs: Try.fold(folder, Ok([]), xs)
    )

def validate_optional(value: Option[T], error_msg: str) -> Result[T, Exception]:
    """Validate an optional value, returning Error if Nothing."""
    return pipe(
        value,
        option.map(Ok),
        option.default_value(Error(ValueError(error_msg)))
    )
