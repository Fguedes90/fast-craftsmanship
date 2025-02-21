"""Type handling utilities."""
from collections.abc import Callable
from typing import TypeVar, Any
from expression import Result, pipe, Try, effect

T = TypeVar('T')

@effect.try_[T]()
def ensure_type(
    value: Any,
    type_constructor: Callable[[Any], T],
    type_name: str,
    validation_fn: Callable[[Any], bool] | None = None,
) -> T:
    """Ensure a value satisfies type and validation requirements using Expression's Try effect.
    
    Args:
        value: Value to validate and cast
        type_constructor: Function to create the type
        type_name: Name of the type for error messages
        validation_fn: Optional validation function
    """
    if validation_fn and not validation_fn(value):
        raise ValueError(f"Invalid {type_name}")
        
    return type_constructor(value)

def map_type(
    f: Callable[[str], Result[str, Exception]],
    type_constructor: Callable[[str], T]
) -> Callable[[T], Result[T, Exception]]:
    """Map a function over a type while preserving its type.
    
    Args:
        f: Function to map over the value
        type_constructor: Constructor for the type
    """
    return lambda x: pipe(
        f(str(x)),
        Try.map(type_constructor)
    )