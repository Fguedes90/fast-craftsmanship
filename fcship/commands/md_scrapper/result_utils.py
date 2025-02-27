"""Result utility functions for the MD scrapper."""

from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

from fcship.utils.error_handling import handle_command_errors

T = TypeVar("T")
P = ParamSpec("P")


def catch_errors(
    exception_type: type[Exception], error_message: str
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator that catches specific exceptions and returns them as Result.Error.
    This is a compatibility wrapper around handle_command_errors."""

    def decorator(fn: Callable[P, T]) -> Callable[P, T]:
        wrapped = handle_command_errors(fn)
        return wrapped

    return decorator


def catch_errors_async(
    exception_type: type[Exception], error_message: str
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """Async version of catch_errors decorator.
    This is a compatibility wrapper around handle_command_errors."""

    def decorator(fn: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        wrapped = handle_command_errors(fn)
        return wrapped

    return decorator
