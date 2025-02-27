"""Type helpers for safe type handling."""

from collections.abc import Callable

from expression import Result, pipe

from fcship.utils.functional import safe_cast
from fcship.utils.type_utils import ensure_type

from .exceptions import ValidationException
from .types import Content, Depth, Filename, Url


def ensure_url(value: str) -> Result[Url, ValidationException]:
    """Ensure a value is a valid URL."""
    return ensure_type(value, Url, "URL")


def ensure_depth(value: int) -> Result[Depth, ValidationException]:
    """Ensure a value is a valid depth."""
    return ensure_type(value, Depth, "depth", lambda x: x >= 0, "Depth cannot be negative")


def ensure_content(value: str) -> Result[Content, ValidationException]:
    """Ensure a value is valid content."""
    return ensure_type(value, Content, "content", lambda x: bool(x), "Content cannot be empty")


def ensure_filename(value: str) -> Result[Filename, ValidationException]:
    """Ensure a value is a valid filename."""
    return ensure_type(value, Filename, "filename", lambda x: bool(x), "Filename cannot be empty")


def map_url(f: Callable[[str], Result[str, Exception]]) -> Callable[[Url], Result[Url, Exception]]:
    """Map a function over a URL while preserving its type."""
    return lambda url: pipe(
        f(url), lambda result: safe_cast(result.ok, Url) if result.is_ok() else result
    )
