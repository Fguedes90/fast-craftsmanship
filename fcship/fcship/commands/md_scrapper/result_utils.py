"""Result transformations and error handling utilities."""
from collections.abc import Awaitable, Callable
from typing import TypeVar, Any
from expression import Result, Ok, Error, pipe
from functools import wraps
from .exceptions import ProcessingException, capture_exception
import logging

A = TypeVar('A')
B = TypeVar('B')

def transform_result(
    transform_fn: Callable[[A], Result[B, ProcessingException]]
) -> Callable[[Result[A, ProcessingException]], Result[B, ProcessingException]]:
    """Transform a Result value while preserving the Railway pattern."""
    def transformer(result: Result[A, ProcessingException]) -> Result[B, ProcessingException]:
        return result.bind(transform_fn)
    return transformer

async def transform_result_async(
    transform_fn: Callable[[A], Awaitable[Result[B, ProcessingException]]]
) -> Callable[[Result[A, ProcessingException]], Awaitable[Result[B, ProcessingException]]]:
    """Transform a Result value asynchronously while preserving the Railway pattern."""
    async def transformer(result: Result[A, ProcessingException]) -> Result[B, ProcessingException]:
        if isinstance(result, Error):
            return result
        return await transform_fn(result.value)
    return transformer

def catch_errors(
    error_type: type[ProcessingException] = ProcessingException,
    error_message: str = "Operation failed"
) -> Callable[[Callable[..., Result[A, ProcessingException]]], Callable[..., Result[A, ProcessingException]]]:
    """Decorator to catch and transform errors into Results."""
    def decorator(
        fn: Callable[..., Result[A, ProcessingException]]
    ) -> Callable[..., Result[A, ProcessingException]]:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Result[A, ProcessingException]:
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
    def decorator(
        fn: Callable[..., Awaitable[Result[A, ProcessingException]]]
    ) -> Callable[..., Awaitable[Result[A, ProcessingException]]]:
        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Result[A, ProcessingException]:
            try:
                return await fn(*args, **kwargs)
            except Exception as e:
                return capture_exception(e, error_type, error_message)
        return wrapper
    return decorator

def log_error(
    result: Result[A, ProcessingException], 
    context: str
) -> Result[A, ProcessingException]:
    """Log error if present and return the original result."""
    if isinstance(result, Error):
        logging.error(f"Error in {context}: {result.error}")
    return result

async def log_error_async(
    result: Result[A, ProcessingException], 
    context: str
) -> Result[A, ProcessingException]:
    """Log error if present and return the original result asynchronously."""
    if isinstance(result, Error):
        logging.error(f"Error in {context}: {result.error}")
    return result

def ensure_ok(
    error_type: type[ProcessingException],
    error_message: str,
    value: A | None = None, 
) -> Result[A, ProcessingException]:
    """Convert an optional value to a Result."""
    return Error(error_type(error_message)) if value is None else Ok(value)

def compose_results(
    *functions: Callable[[A], Result[A, ProcessingException]]
) -> Callable[[A], Result[A, ProcessingException]]:
    """Compose multiple Result-returning functions."""
    def compose_two(
        f: Callable[[A], Result[A, ProcessingException]], 
        g: Callable[[A], Result[A, ProcessingException]]
    ) -> Callable[[A], Result[A, ProcessingException]]:
        return lambda x: g(x).bind(f)
    
    from functools import reduce
    return reduce(compose_two, functions)