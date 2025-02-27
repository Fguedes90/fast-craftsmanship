"""Shared types and constants for TUI components."""

from typing import Literal, Protocol

from expression import tagged_union
from rich.console import Console

# Create console instance
console = Console()


# Protocol for console abstraction
class ConsoleProtocol(Protocol):
    def print(self, *args, **kwargs) -> None: ...


@tagged_union
class DisplayError:
    """Display-related errors"""

    tag: Literal["validation", "rendering"]
    validation: str = None
    rendering: tuple[str, Exception] = None

    @staticmethod
    def Validation(msg: str) -> "DisplayError":
        return DisplayError(tag="validation", validation=msg)

    @staticmethod
    def Rendering(msg: str, error: Exception) -> "DisplayError":
        return DisplayError(tag="rendering", rendering=(msg, error))
