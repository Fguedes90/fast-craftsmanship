# Composição Funcional com pipe e pipeline

## Usando pipe para Encadear Funções

### O que é
A função `pipe` permite passar um valor através de uma série de funções, aplicando cada função ao resultado da anterior.

### Por que é importante para ROP
Torna o código mais legível, expressivo e fácil de seguir. Em vez de aninhar chamadas de função, você as encadeia em uma ordem lógica.

### Exemplo (sem Result ainda)

```python
from expression import pipe

def add_one(x: int) -> int:
    return x + 1

def multiply_by_two(x: int) -> int:
    return x * 2

result = pipe(
    5,
    add_one,
    multiply_by_two
)
print(result)  # 12
```

## Usando pipeline para Compor Funções Result

### O que é
A função `pipeline` é especificamente projetada para compor funções que retornam Result. Ela lida automaticamente com a propagação de erros. Se uma função no pipeline retornar Error, o restante do pipeline é ignorado e o Error é retornado.

### Por que é importante para ROP
Simplifica o tratamento de erros em pipelines. Você não precisa verificar o resultado de cada função individualmente.

### Kleisli Composition
`pipeline` implementa a Kleisli Composition, que é uma forma elegante de compor funções que retornam valores "wrapped" (neste caso, Result).

### Exemplo

```python
from expression import pipeline, Result, Ok, Error

def validate_age(age: int) -> Result[int, str]:
    if age < 0:
        return Error("Idade inválida")
    elif age > 150:
        return Error("Idade muito alta")
    else:
        return Ok(age)

def grant_access(age: int) -> Result[str, str]:
    if age >= 18:
        return Ok("Acesso concedido")
    else:
        return Error("Acesso negado")

access_pipeline = pipeline(
    validate_age,
    grant_access
)

result1 = access_pipeline(25)  # Ok("Acesso concedido")
result2 = access_pipeline(-5)  # Error("Idade inválida")
result3 = access_pipeline(15)  # Error("Acesso negado")

print(result1)
print(result2)
print(result3)
```

## Como pipeline Substitui if/else

Em vez de usar if/else para verificar o resultado de cada função e decidir o que fazer em seguida, você define um pipeline de funções Result. O pipeline cuida da lógica de controle de fluxo para você.

```python
# Sem pipeline (com if/else)
def process_data(data):
    result1 = validate_data(data)
    if is_ok(result1):
        result2 = transform_data(result1.value)
        if is_ok(result2):
            result3 = save_data(result2.value)
            if is_ok(result3):
                return Ok("Sucesso")
            else:
                return result3  # Propaga o erro de save_data
        else:
            return result2  # Propaga o erro de transform_data
    else:
        return result1  # Propaga o erro de validate_data

# Com pipeline
def process_data_pipeline(data):
    return pipeline(
        validate_data,
        transform_data,
        save_data
    )(data)
```

## Próximos Passos

Agora você tem as ferramentas essenciais para ROP: Result, pipe e pipeline. O próximo tópico abordará Option, que pode ser útil em cenários específicos onde você precisa lidar com a ausência de valores além dos erros representados por Result.