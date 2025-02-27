"""Error types for the UI module."""

from typing import Literal

from expression import tagged_union


@tagged_union
class DisplayError:
    """Represents display-related errors."""

    tag: Literal["validation", "rendering", "interaction", "timeout", "execution", "input"]
    validation: str | None = None
    rendering: tuple[str, Exception] | None = None
    interaction: tuple[str, Exception] | None = None
    timeout: tuple[str, Exception] | None = None
    execution: tuple[str, str] | None = None
    input: tuple[str, str] | None = None

    @staticmethod
    def Validation(message: str) -> "DisplayError":
        """Create validation error."""
        return DisplayError(tag="validation", validation=message)

    @staticmethod
    def Rendering(message: str, error: Exception) -> "DisplayError":
        """Create rendering error."""
        return DisplayError(tag="rendering", rendering=(message, error))

    @staticmethod
    def Interaction(message: str, error: Exception) -> "DisplayError":
        """Create interaction error."""
        return DisplayError(tag="interaction", interaction=(message, error))

    @staticmethod
    def Timeout(message: str, error: Exception) -> "DisplayError":
        """Create timeout error."""
        return DisplayError(tag="timeout", timeout=(message, error))

    @staticmethod
    def ExecutionError(message: str, error: str) -> "DisplayError":
        """Create execution error."""
        return DisplayError(tag="execution", execution=(message, error))

    @staticmethod
    def Input(message: str, error: str) -> "DisplayError":
        """Create input error."""
        return DisplayError(tag="input", input=(message, error))

    def __str__(self) -> str:
        """Convert error to string."""
        match self:
            case DisplayError(tag="validation", validation=msg):
                return f"Validation Error: {msg}"
            case DisplayError(tag="rendering", rendering=(msg, exc)):
                return f"Display Error: {msg} - {exc!s}"
            case DisplayError(tag="interaction", interaction=(msg, exc)):
                return f"Input Error: {msg} - {exc!s}"
            case DisplayError(tag="timeout", timeout=(msg, exc)):
                return f"Timeout Error: {msg} - {exc!s}"
            case DisplayError(tag="execution", execution=(msg, err)):
                return f"Execution Error: {msg} - {err}"
            case DisplayError(tag="input", input=(msg, err)):
                return f"Input Error: {msg} - {err}"
            case _:
                return "Unknown Error"
