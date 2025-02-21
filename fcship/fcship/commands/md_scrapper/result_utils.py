"""Result transformations and error handling utilities."""
from collections.abc import Awaitable, Callable
from typing import TypeVar, Any
from expression import Result
from functools import wraps
from fcship.utils.functional import (
    transform_result,
    transform_result_async,
    catch_errors as catch_base_errors,
    catch_errors_async as catch_base_errors_async,
    handle_error as base_handle_error,
    log_and_continue
)
from .exceptions import ProcessingException, capture_exception
import logging

A = TypeVar('A')
B = TypeVar('B')

# Re-export shared utilities with scraper-specific error types
def catch_errors(
    error_type: type[ProcessingException] = ProcessingException,
    error_message: str = "Operation failed"
) -> Callable[[Callable[..., Result[A, ProcessingException]]], Callable[..., Result[A, ProcessingException]]]:
    """Decorator to catch and transform errors into Results."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                return capture_exception(e, error_type, error_message)
        return wrapper
    return decorator

def catch_errors_async(
    error_type: type[ProcessingException] = ProcessingException,
    error_message: str = "Operation failed"
) -> Callable[[Callable[..., Awaitable[Result[A, ProcessingException]]]], 
              Callable[..., Awaitable[Result[A, ProcessingException]]]]:
    """Decorator to catch and transform errors into Results asynchronously."""
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                return capture_exception(e, error_type, error_message)
        return wrapper
    return decorator

def handle_error(error: Exception, context: str = "") -> Result[Any, ProcessingException]:
    """Handle errors with scraper-specific error type."""
    return base_handle_error(ProcessingException(str(error), error), context)