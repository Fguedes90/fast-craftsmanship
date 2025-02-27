"""Validation utilities."""

from collections.abc import Callable, Sequence
from typing import TypeVar

import typer

from expression import Error, Ok, Option, Result, pipe

from .functional import option_to_result

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None,
) -> Result[str, Exception]:
    """Validate command operation and arguments using Expression's Try effect."""
    valid_ops_message = ", ".join(valid_operations)

    def check_operation(op: str) -> Result[str, Exception]:
        return (
            Ok(op)
            if op in valid_operations
            else Error(
                typer.BadParameter(
                    f"Invalid operation: {op}. Valid operations: {valid_ops_message}"
                )
            )
        )

    def check_name_requirement(op: str) -> Result[str, Exception]:
        return (
            Error(typer.BadParameter(f"Operation '{op}' requires a name parameter"))
            if requires_name and op in requires_name and not name
            else Ok(op)
        )

    return pipe(
        Ok(operation),
        lambda res: res.bind(check_operation),
        lambda res: res.bind(check_name_requirement),
    )


def validate(validator: Callable[[T], bool], error_msg: str) -> Callable[[T], Result[T, Exception]]:
    """Create a validation function that returns a Result."""
    return lambda value: Ok(value) if validator(value) else Error(ValueError(error_msg))


def compose_validations(
    *validators: Callable[[T], Result[T, Exception]],
) -> Callable[[T], Result[T, Exception]]:
    """Compose multiple validation functions into a single validation."""
    from functools import reduce

    return lambda value: reduce(lambda acc, v: acc.bind(v), validators, Ok(value))


def validate_optional(value: Option[T], error_msg: str) -> Result[T, Exception]:
    """Validate an optional value, returning Error if Nothing."""
    return option_to_result(value, error_msg)


def sequence_validations(
    validations: Sequence[Result[T, Exception]],
) -> Result[Sequence[T], Exception]:
    """Aggregate a sequence of validation Results into a single Result containing all valid values.
    Short-circuits on the first validation error encountered."""
    from functools import reduce

    return reduce(
        lambda acc, r: acc.bind(lambda xs: r.map(lambda x: xs + [x])), validations, Ok([])
    ).bind(lambda lst: Ok(lst))
