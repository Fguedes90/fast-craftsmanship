"""Custom exceptions for Railway Oriented Programming."""

from expression import Error, Result


class ScraperException(Exception):
    """Base exception for scraper operations."""

    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def to_result(self) -> Result[None, "ScraperException"]:
        """Convert exception to Result type."""
        return Error(self)


class ValidationException(ScraperException):
    """Exception for validation errors."""

    pass


class ContentException(ScraperException):
    """Exception for content processing errors."""

    pass


class NetworkException(ScraperException):
    """Exception for network related errors."""

    pass


class ProcessingException(ScraperException):
    """Exception for general processing errors."""

    pass


def capture_exception(
    error: Exception, error_type: type[ScraperException], message: str
) -> Result[None, ScraperException]:
    """Capture and convert an exception to a Result type."""
    return Error(error_type(message, error))


def ensure_result(value: Result | None, error_message: str) -> Result:
    """Ensure a value is a Result type."""
    return Error(ProcessingException(error_message)) if value is None else value
