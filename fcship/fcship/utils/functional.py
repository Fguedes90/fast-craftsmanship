"""Functional programming utilities."""
from collections.abc import Awaitable, Callable, Sequence
from typing import TypeVar, Any, ParamSpec
import asyncio
import functools
from expression import Result, Ok, Error, Option, Block

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
P = ParamSpec('P')


def lift_option(fn: Callable[P, Option[A]]) -> Callable[P, Result[A, Exception]]:
    """
    Eleva uma função que retorna um Option para uma função que retorna um Result.
    
    Se a função original retornar um Option com valor (Some), converte para Ok(valor).
    Caso contrário, retorna um Error com a mensagem "No value present".
    """
    @functools.wraps(fn)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> Result[A, Exception]:
        opt: Option[A] = fn(*args, **kwargs)
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
    values = Block.of_seq([result.ok for result in results if not result.is_error()])
    return Ok(values)

def tap(fn: Callable[[A], Any]) -> Callable[[A], A]:
    """
    Cria uma função que executa um efeito colateral e retorna o mesmo valor inalterado.
    
    Útil para inserir chamadas de debug, log ou outras operações de side effect em cadeias
    de transformações puras.
    """
    @functools.wraps(fn)
    def tapped(value: A) -> A:
        fn(value)
        return value
    return tapped

def tap_async(fn: Callable[[A], Awaitable[Any]]) -> Callable[[A], Awaitable[A]]:
    """
    Cria uma função assíncrona que executa um efeito colateral e retorna o mesmo valor inalterado.
    
    Essa função é útil para incorporar operações assíncronas (como log assíncrono ou
    atualização de métricas) em cadeias de operações.
    """
    @functools.wraps(fn)
    def tapped(value: A) -> Awaitable[A]:
        async def inner() -> A:
            await fn(value)
            return value
        return inner()
    return tapped

from expression import Nothing  # adicione se necessário

def option_to_result(opt: Option[A], error_msg: str) -> Result[A, Exception]:
    """
    Converte uma instância de Option em um Result.
    
    Se o Option não contiver valor (ou seja, for None), retorna um Error com a mensagem
    de erro fornecida. Caso contenha valor, retorna um Ok contendo o valor.
    """
    return Error(ValueError(error_msg)) if opt.is_none() else Ok(opt.value)
