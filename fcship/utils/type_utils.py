"""Utilitários para manipulação de tipos."""

from collections.abc import Callable
from typing import Any, TypeVar

import typer

from expression import Error, Ok, Result

T = TypeVar("T")


def ensure_type(
    value: Any,
    type_constructor: Callable[[Any], T],
    type_name: str,
    validation_fn: Callable[[Any], bool] | None = None,
) -> T:
    """
    Garante que um valor atenda aos requisitos de tipo e validação.

    Args:
        value: Valor a ser validado e convertido.
        type_constructor: Função para construir o tipo desejado.
        type_name: Nome do tipo, usado nas mensagens de erro.
        validation_fn: Função opcional para validar o valor.

    Returns:
        O valor convertido para o tipo especificado.

    Raises:
        ValueError: Se a função de validação indicar que o valor é inválido.
    """
    if validation_fn is not None:
        validation_result = validation_fn(value)
        if isinstance(validation_result, bool):
            if not validation_result:
                raise ValueError(f"Valor inválido para {type_name}")
        elif not validation_result.is_ok():
            raise ValueError(validation_result.error)
    return type_constructor(value)


def map_type(
    f: Callable[[str], Result[str, Exception]], type_constructor: Callable[[str], T]
) -> Callable[[T], Result[T, Exception]]:
    """
    Aplica uma função a um valor (convertido para string) e reconstrói o tipo,
    preservando a tipagem original.

    Args:
        f: Função que transforma uma string em um Result contendo uma string ou uma exceção.
        type_constructor: Construtor para converter a string de volta para o tipo desejado.

    Returns:
        Uma função que, dado um valor do tipo T, retorna um Result[T, Exception].
    """

    def mapper(x: T) -> Result[T, Exception]:
        try:
            value_str = x.value
        except AttributeError:
            value_str = str(x)
        return f(value_str).map(lambda s: type_constructor(s))

    return mapper


def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None,
) -> Result[str, Exception]:
    """
    Valida uma operação de comando e os seus argumentos, garantindo que a operação
    esteja na lista de operações válidas e que, se necessário, o parâmetro 'name' seja fornecido.

    Args:
        operation: Operação a ser validada.
        valid_operations: Lista das operações consideradas válidas.
        name: Nome associado à operação (opcional).
        requires_name: Lista de operações que exigem o parâmetro 'name'.

    Returns:
        A própria operação, se for válida.

    Raises:
        typer.BadParameter: Se a operação não for válida ou se faltar o parâmetro 'name'
                            para operações que o requerem.
    """
    if operation not in valid_operations:
        valid_ops = ", ".join(valid_operations)
        return Error(
            typer.BadParameter(f"Operação inválida: {operation}. Operações válidas: {valid_ops}")
        )
    if requires_name is not None and operation in requires_name and not name:
        return Error(typer.BadParameter(f"A operação '{operation}' requer o parâmetro 'name'."))
    return Ok(operation)
