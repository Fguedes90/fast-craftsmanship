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
    Works with both sync and async functions.
    This is an alias for @effect.try_ to unify the usage in sync/async functions.
    """
    if asyncio.iscoroutinefunction(fn):
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> A:
            return await fn(*args, **kwargs)
        return wrapper
    return fn

def lift_option(fn: Callable[P, Option[A]]) -> Callable[P, Result[A, Exception]]:
    """Lift an Option-returning function into a Result-returning function."""
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> Result[A, Exception]:
        opt = fn(*args, **kwargs)
        return option_to_result(opt, "No value present")
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
        if result.is_error():
            return result
        values.append(result.ok)
    return Ok(values)

def tap(fn: Callable[[A], Any]) -> Callable[[A], A]:
    """Create a function that runs a side effect but returns the original value."""
    def tapped(value: A) -> A:
        fn(value)
        return value
    return tapped

def tap_async(fn: Callable[[A], Awaitable[Any]]) -> Callable[[A], Awaitable[A]]:
    """Create an async function that runs a side effect but returns the original value."""
    def tapped(value: A) -> Awaitable[A]:
        async def inner() -> A:
            await fn(value)
            return value
        return inner()
    return tapped

from expression import Nothing  # adicione se necessário

def option_to_result(opt: Option[A], error_msg: str) -> Result[A, Exception]:
    """Converte um Option em Result, retornando um Error com a mensagem fornecida caso seja Nothing."""
    if opt == Nothing:
        return Error(ValueError(error_msg))
    return Ok(opt.value)
