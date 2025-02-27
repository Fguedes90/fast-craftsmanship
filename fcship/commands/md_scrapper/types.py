"""Common types and definitions for the scraper."""

from typing import NewType, TypeVar

from expression import Error, Result

# Type aliases
Url = NewType("Url", str)
Depth = NewType("Depth", int)
Content = NewType("Content", str)
Filename = NewType("Filename", str)
HtmlContent = NewType("HtmlContent", str)
MarkdownContent = NewType("MarkdownContent", str)

# Generic type variables
A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

# Common result types
ScraperResult = Result[None, Exception]
ContentResult = Result[tuple[Content, Filename], Exception]
LinkResult = Result[list[tuple[Url, Depth]], Exception]


# Error definitions
class ScraperError(Exception):
    """Base error for scraper operations."""

    pass


class ContentExtractionError(ScraperError):
    """Error during content extraction."""

    pass


class ValidationError(ScraperError):
    """Error during validation."""

    pass


class ProcessingError(ScraperError):
    """Error during page processing."""

    pass


def make_error(error_type: type[ScraperError], message: str) -> Error:
    """Create a typed error result."""
    return Error(error_type(message))
