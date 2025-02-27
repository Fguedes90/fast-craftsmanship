# Try: Simplificando Result com Exceções

## O que é Try

- Try é um tipo similar a Result, mas com o tipo de erro fixado em Exception.
- É essencialmente um alias para `Result[TSource, Exception]`.
- **Por que usar Try**: Simplifica o código quando você está lidando principalmente com exceções. Você não precisa especificar o tipo de erro repetidamente.

## Success e Failure

`Success(value)` representa um sucesso, e `Failure(exception)` representa uma falha (uma exceção).

```python
from expression import Try, Success, Failure

def divide(a: float, b: float) -> Try[float]:
    try:
        return Success(a / b)
    except Exception as ex:
        return Failure(ex)

result = divide(10, 2)  # Success(5.0)
result = divide(10, 0)  # Failure(ZeroDivisionError('division by zero'))
```

## Como Try se Compara a Result

- Try é mais conveniente quando você está convertendo código que já usa exceções. Você simplesmente captura a exceção e retorna Failure.
- Result é mais flexível quando você precisa representar diferentes tipos de erros, não apenas exceções.

## Usando Try com pipeline

`pipeline` funciona perfeitamente com funções que retornam Try.

```python
from expression import pipeline, Try, Success, Failure

def parse_int(s: str) -> Try[int]:
    try:
        return Success(int(s))
    except ValueError as ex:
        return Failure(ex)

def add_one(x: int) -> Try[int]:
    return Success(x + 1)

process_pipeline = pipeline(
    parse_int,
    add_one
)

result1 = process_pipeline("10")  # Success(11)
result2 = process_pipeline("abc")  # Failure(ValueError("invalid literal for int()..."))

print(result1)
print(result2)
```

## Usando @effect.result com Try

Você ainda pode usar `@effect.result` com Try, mas precisa especificar Exception como o tipo de erro:

```python
from expression import effect, Try, Success, Failure

@effect.result[int, Exception]()
def my_function(s: str):
    x = yield from Success(10)
    y = yield from Try(int(s))
    return x + y

result1 = my_function("5")  # Ok(15)
result2 = my_function("abc")  # Error(ValueError("invalid literal for int()..."))
```

## Próximos Passos

Agora você tem uma compreensão de Try e como ele se relaciona com Result. O próximo e último tópico abordará padrões e boas práticas para usar expression com ROP de forma eficaz.

## Dicas de Uso

1. Use Try quando:
   - Você está convertendo código existente que usa try/except
   - Todas as suas falhas são exceções
   - Você não precisa de tipos de erro personalizados

2. Use Result quando:
   - Você precisa de tipos de erro personalizados
   - Você quer ser mais explícito sobre os tipos de falha possíveis
   - Você está construindo uma API que outros desenvolvedores usarão