# Python Functional Guide
#
# Este guia apresenta exemplos de como desenvolver com uma abordagem funcional
# que é facilmente testável e legível. Para cada conceito, são apresentados exemplos do
# "como NÃO fazer" e "como fazer". Utilize os conceitos da biblioteca Expression e as
# práticas funcionais recomendadas.
#
# ------------------------------------------------------------------------------
# Seção 1: Funções Puras vs. Funções Impuras
# ------------------------------------------------------------------------------
#
# NÃO FAZER: Função com efeitos colaterais (ex.: impressão) misturados com lógica.
from expression import pipe

add_and_print = lambda a, b: pipe(a + b, lambda result: (print("Resultado (impuro):", result), result)[1])

# FAZER: Função pura que apenas retorna o resultado.
add = lambda a, b: a + b

# ------------------------------------------------------------------------------
# Seção 2: Composição Funcional com `pipe` e `compose`
# ------------------------------------------------------------------------------
from expression import pipe, compose, Ok, Error, Try

# NÃO FAZER (exemplo ruim com aninhamento):
calculate_bad = lambda x: (lambda a: (lambda b: a + b)(x * 2))(x + 3)

# FAZER: Utilizando pipe para compor de forma legível:
calculate_good = lambda x: pipe(x, (lambda val: val + 3), (lambda val: val * 2))

# Alternativamente, utilizando compose para composição da esquerda para a direita:
calculate_compose = lambda x: compose((lambda v: v + 3), (lambda v: v * 2))(x)

# ------------------------------------------------------------------------------
# Seção 3: Tratamento de Erros com Try e Option
# ------------------------------------------------------------------------------
from expression import effect, option, Nothing, Some

# NÃO FAZER: Divisão sem tratamento de erro.
divide_bad = lambda a, b: a / b

# FAZER: Utilizando pipe para evitar aninhamento e tratar o erro.
__raise = lambda e: (_ for _ in ()).throw(e)
divide = effect.try_[float](lambda a, b:
    pipe((a, b), lambda t: t[0] / t[1] if t[1] != 0
         else __raise(ValueError("Divisão por zero não é permitida")))
)

# Exemplo com Option, sem aninhar chamadas.
get_item_option = lambda lst, index: Some(lst[index]) if 0 <= index < len(lst) else Nothing

# ------------------------------------------------------------------------------
# Seção 4: Utilitários de Ordem Superior: tap e map_type
# ------------------------------------------------------------------------------
def log_side_effect(value):
    # Exemplo de efeito colateral: log (pode ser substituído por um logger real)
    print("Log:", value)fcship/fcship/utils/type_utils.py
<source>python
<<<<<<< SEARCH
from collections.abc import Callable
from typing import TypeVar, Any
from expression import Result, pipe, Try, effect

T = TypeVar('T')

@effect.try_[T]()
def ensure_type(
    value: Any,
    type_constructor: Callable[[Any], T],
    type_name: str,
    validation_fn: Callable[[Any], bool] | None = None,
) -> T:
    """Ensure a value satisfies type and validation requirements using Expression's Try effect.

    Args:
        value: Value to validate and cast
        type_constructor: Function to create the type
        type_name: Name of the type for error messages
        validation_fn: Optional validation function
    """
    if validation_fn and not validation_fn(value):
        raise ValueError(f"Invalid {type_name}")

    return type_constructor(value)

def map_type(
    f: Callable[[str], Result[str, Exception]],
    type_constructor: Callable[[str], T]
) -> Callable[[T], Result[T, Exception]]:
    """Map a function over a type while preserving its type.

    Args:
        f: Function to map over the value
        type_constructor: Constructor for the type
    """
    return lambda x: pipe(
        f(str(x)),
        Try.map(type_constructor)
    )

def validate_operation(
    operation: str,
    valid_operations: list[str],
    name: str | None = None,
    requires_name: list[str] | None = None
) -> str:
    """Validate command operation and arguments using Expression's Try effect."""
    if operation not in valid_operations:
        valid_ops = ", ".join(valid_operations)
        raise typer.BadParameter(
            f"Invalid operation: {operation}. Valid operations: {valid_ops}"
        )

    if requires_name and operation in requires_name and not name:
        raise typer.BadParameter(
            f"Operation '{operation}' requires a name parameter"
        )

    return operation
