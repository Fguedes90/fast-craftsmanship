# Efeitos com effect

## O que são Efeitos

Em programação funcional, um "efeito" é uma computação que interage com o mundo externo (I/O, estado mutável, etc.). A biblioteca expression usa o termo "efeito" para se referir a computações que envolvem tipos como Option e Result, permitindo que você escreva código que se parece com código imperativo, mas que ainda é funcional e seguro.

## Usando @effect.result

### O que faz
O decorador `@effect.result` transforma uma função em uma computação que retorna um Result. Dentro da função, você pode usar `yield from` para "desempacotar" Results. Se um Error for encontrado, a função é interrompida e o Error é retornado.

### Por que é útil para ROP
Simplifica o encadeamento de operações Result, tornando o código mais legível e menos verboso. Elimina a necessidade de aninhar chamadas de bind ou usar match repetidamente.

### Exemplo

```python
from expression import effect, Result, Ok, Error

def validate_age(age: int) -> Result[int, str]:
    if age < 0:
        return Error("Idade inválida")
    else:
        return Ok(age)

def grant_access(age: int) -> Result[str, str]:
    if age >= 18:
        return Ok("Acesso concedido")
    else:
        return Error("Acesso negado")

@effect.result[str, str]()  # Tipo de sucesso: str, tipo de erro: str
def access_pipeline(age: int):
    validated_age = yield from validate_age(age)
    access_result = yield from grant_access(validated_age)
    return access_result

result1 = access_pipeline(25)  # Ok("Acesso concedido")
result2 = access_pipeline(-5)  # Error("Idade inválida")

print(result1)
print(result2)
```

## yield from para Desempacotar Efeitos

- `yield from` é a chave para usar `@effect.result`. Ele "desempacota" o valor dentro de um Result.
- Se o Result for Ok, o valor é atribuído à variável.
- Se o Result for Error, a função é interrompida e o Error é retornado.
- **Importante**: A função decorada com `@effect.result` deve retornar um Result.

## Usando @effect.option

Funciona de forma similar a `@effect.result`, mas para Option. Se um Nothing for encontrado, a função é interrompida e Nothing é retornado.

```python
from expression import effect, Option, Some, Nothing

def get_name(user_id: int) -> Option[str]:
    if user_id == 1:
        return Some("Alice")
    else:
        return Nothing

@effect.option[str]()
def greet(user_id: int):
    name = yield from get_name(user_id)
    return f"Olá, {name}!"

greeting1 = greet(1)  # Some("Olá, Alice!")
greeting2 = greet(2)  # Nothing

print(greeting1)
print(greeting2)
```

## Próximos Passos

Agora você tem uma compreensão de como usar `@effect.result` e `@effect.option` para simplificar o encadeamento de operações. O próximo tópico abordará Try, que é uma forma simplificada de Result quando você está lidando principalmente com exceções.