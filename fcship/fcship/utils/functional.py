"""Functional programming utilities."""
from collections.abc import Awaitable, Callable, Sequence
from typing import TypeVar, Any, overload, ParamSpec
import asyncio
from expression import Result, Ok, Error, effect, pipe, option, Option

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
P = ParamSpec('P')

@overload
def catch_errors(fn: Callable[P, A]) -> A: ...

@overload
def catch_errors(fn: Callable[P, Awaitable[A]]) -> Awaitable[A]: ...

@effect.try_[A]()
def catch_errors(fn: Callable[P, A] | Callable[P, Awaitable[A]]) -> A | Awaitable[A]:
    """Decorator to catch and transform errors into Results using Expression's Try effect.
    Works with both sync and async functions."""
    if asyncio.iscoroutinefunction(fn):
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> A:
            return await fn(*args, **kwargs)
        return wrapper
    return fn

def lift_option(fn: Callable[P, Option[A]]) -> Callable[P, Result[A, Exception]]:
    """Lift an Option-returning function into a Result-returning function."""
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> Result[A, Exception]:
        opt = fn(*args, **kwargs)
        return pipe(
            opt,
            option.map(Ok),
            option.default_value(Error(ValueError("No value present")))
        )
    return wrapped

async def collect_results(results: Sequence[Awaitable[Result[A, Exception]]]) -> Result[Sequence[A], Exception]:
    """Collect multiple async Results into a single Result containing all values.
    Short-circuits on first Error."""
    try:
        completed = await asyncio.gather(*results)
        return sequence_results(completed)
    except Exception as e:
        return Error(e)

def sequence_results(results: Sequence[Result[A, Exception]]) -> Result[Sequence[A], Exception]:
    """Convert a sequence of Results into a Result of sequence.
    Short-circuits on first Error."""
    values: list[A] = []
    for result in results:
        match result:
            case Ok(value):
                values.append(value)
            case Error(e):
                return Error(e)
    return Ok(values)

def tap(fn: Callable[[A], Any]) -> Callable[[A], A]:
    """Create a function that runs a side effect but returns the original value."""
    def tapped(value: A) -> A:
        fn(value)
        return value
    return tapped

async def tap_async(fn: Callable[[A], Awaitable[Any]]) -> Callable[[A], Awaitable[A]]:
    """Create an async function that runs a side effect but returns the original value."""
    def tapped(value: A) -> Awaitable[A]:
        async def inner(value: A) -> A:
            await fn(value)
            return value
        return inner(value)
    return tapped
