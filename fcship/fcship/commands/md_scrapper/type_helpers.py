"""Type helpers for safe type handling."""
from typing import TypeVar, Callable, Any
from expression import Result, Ok, Error, pipe
from .types import Url, Depth, Content, Filename
from .exceptions import ValidationException

T = TypeVar('T')

def safe_cast(value: Any, type_constructor: Callable[[Any], T]) -> Result[T, ValidationException]:
    """Safely cast a value to a type."""
    try:
        return Ok(type_constructor(value))
    except (ValueError, TypeError) as e:
        return Error(ValidationException(f"Failed to cast {value} to {type_constructor.__name__}", e))

def ensure_url(value: str) -> Result[Url, ValidationException]:
    """Ensure a value is a valid URL."""
    return safe_cast(value, Url)

def ensure_depth(value: int) -> Result[Depth, ValidationException]:
    """Ensure a value is a valid depth."""
    if value < 0:
        return Error(ValidationException(f"Depth cannot be negative: {value}"))
    return safe_cast(value, Depth)

def ensure_content(value: str) -> Result[Content, ValidationException]:
    """Ensure a value is valid content."""
    if not value:
        return Error(ValidationException("Content cannot be empty"))
    return safe_cast(value, Content)

def ensure_filename(value: str) -> Result[Filename, ValidationException]:
    """Ensure a value is a valid filename."""
    if not value:
        return Error(ValidationException("Filename cannot be empty"))
    return safe_cast(value, Filename)

def map_url(f: Callable[[str], Result[str, Exception]]) -> Callable[[Url], Result[Url, Exception]]:
    """Map a function over a URL while preserving its type."""
    return lambda url: pipe(
        f(url),
        lambda result: safe_cast(result.value, Url) if isinstance(result, Ok) else result
    )