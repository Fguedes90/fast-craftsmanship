"""Utility functions for functional operations."""
import logging
from typing import TypeVar, Callable, Any, Awaitable
from expression import pipe, Result, Ok, Error, option, Some, Nothing
from functools import reduce
import asyncio

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

def compose_results(*functions: Callable[[Any], Result[Any, Exception]]) -> Callable[[Any], Result[Any, Exception]]:
    """Compose multiple Result-returning functions."""
    def compose_two(f: Callable[[B], Result[C, Exception]], 
                   g: Callable[[A], Result[B, Exception]]) -> Callable[[A], Result[C, Exception]]:
        return lambda x: pipe(
            g(x),
            lambda r: r.bind(f)
        )
    return reduce(compose_two, functions)

def sequence_results(results: list[Result[A, Exception]]) -> Result[list[A], Exception]:
    """Convert a list of Results into a Result of list."""
    def folder(acc: Result[list[A], Exception], item: Result[A, Exception]) -> Result[list[A], Exception]:
        return pipe(
            acc,
            lambda xs: pipe(
                item,
                lambda x: Ok([*xs, x]) if isinstance(acc, Ok) else Error(acc.error)
            )
        )
    return reduce(folder, results, Ok([]))

def traverse_option(xs: list[A], f: Callable[[A], option[B]]) -> option[list[B]]:
    """Map a function over a list and sequence the results."""
    results = [f(x) for x in xs]
    return pipe(
        results,
        lambda rs: Some([r.value for r in rs]) if all(isinstance(r, Some) for r in rs) else Nothing
    )

async def pipe_async(*functions: Callable[[Any], Awaitable[Result[Any, Exception]]]) -> Callable[[Any], Awaitable[Result[Any, Exception]]]:
    """Compose multiple async Result-returning functions."""
    async def compose_two_async(f: Callable[[B], Awaitable[Result[C, Exception]]], 
                                  g: Callable[[A], Awaitable[Result[B, Exception]]]) -> Callable[[A], Awaitable[Result[C, Exception]]]:
        async def composed(x: A) -> Result[C, Exception]:
            result_b = await g(x)
            return result_b if isinstance(result_b, Error) else await f(result_b.value)

        return composed

    return reduce(compose_two_async, functions)

def handle_error(error: Exception, context: str = "") -> Result[Any, Exception]:
    """Handle errors in a functional way."""
    logging_msg = f"Error in {context}: {str(error)}" if context else str(error)
    logging.error(logging_msg)
    return Error(error)

def log_and_continue(result: Result[A, Exception], context: str = "") -> Result[A, Exception]:
    """Log error and continue with the result."""
    if isinstance(result, Error):
        logging.warning(f"Non-critical error in {context}: {str(result.error)}")
    return result

def ensure_async(value: Result[A, Exception]) -> Awaitable[Result[A, Exception]]:
    """Convert a Result to an async Result."""
    return asyncio.create_task(asyncio.sleep(0, result=value))