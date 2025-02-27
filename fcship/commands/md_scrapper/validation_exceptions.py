"""Validation specific exceptions."""

from dataclasses import dataclass
from typing import Any

from .exceptions import ScraperException


@dataclass
class ValidationError:
    """Validation error details."""

    field: str
    message: str
    value: Any | None = None


class ConfigValidationException(ScraperException):
    """Exception for configuration validation errors."""

    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
        messages = [f"{e.field}: {e.message}" for e in errors]
        super().__init__(f"Configuration validation failed: {'; '.join(messages)}")


class UrlValidationException(ScraperException):
    """Exception for URL validation errors."""

    def __init__(self, url: str, reason: str):
        self.url = url
        self.reason = reason
        super().__init__(f"Invalid URL '{url}': {reason}")


class SelectorValidationException(ScraperException):
    """Exception for CSS selector validation errors."""

    def __init__(self, selector: str, reason: str):
        self.selector = selector
        self.reason = reason
        super().__init__(f"Invalid selector '{selector}': {reason}")


class PathValidationException(ScraperException):
    """Exception for path validation errors."""

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Invalid path '{path}': {reason}")
