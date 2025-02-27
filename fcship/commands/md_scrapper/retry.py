"""Retry handling with functional approach."""

import asyncio

from collections.abc import Awaitable, Callable
from typing import TypeVar

from expression import Error, Ok, Result

from fcship.utils.functional import catch_errors_async

from .exceptions import NetworkException, ProcessingException

T = TypeVar("T")
Operation = Callable[..., Awaitable[Result[T, ProcessingException]]]


async def with_retry(
    operation: Operation,
    max_retries: int,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs,
) -> Result[T, ProcessingException]:
    """Execute operation with exponential backoff retry."""
    delay = initial_delay
    last_error = None

    for attempt in range(max_retries):
        try:
            result = await operation(*args, **kwargs)
            if isinstance(result, Ok):
                return result
            last_error = result.error

            # Only retry on network errors
            if not isinstance(last_error, NetworkException):
                return result

        except Exception as e:
            last_error = e

        if attempt < max_retries - 1:
            await asyncio.sleep(delay)
            delay = min(delay * backoff_factor, max_delay)

    return Error(ProcessingException(f"Operation failed after {max_retries} attempts", last_error))


@catch_errors_async(NetworkException, "Network operation failed")
async def with_timeout(
    operation: Operation, timeout: float, *args, **kwargs
) -> Result[T, ProcessingException]:
    """Execute operation with timeout."""
    try:
        return await asyncio.wait_for(operation(*args, **kwargs), timeout=timeout)
    except TimeoutError as e:
        return Error(NetworkException(f"Operation timed out after {timeout} seconds", e))


async def retry_with_timeout(
    operation: Operation, max_retries: int, timeout: float, *args, **kwargs
) -> Result[T, ProcessingException]:
    """Combine retry and timeout handling."""
    return await with_retry(lambda: with_timeout(operation, timeout), max_retries, *args, **kwargs)
