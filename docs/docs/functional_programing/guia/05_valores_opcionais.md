# Gerenciando Valores Opcionais com Option

## O tipo Option[T]

### O que é
Um tipo que representa um valor que pode ou não estar presente. É usado para lidar com a possibilidade de um valor estar ausente sem lançar exceções ou usar None.

### Some(value) e Nothing
`Some(value)` representa um valor presente, e `Nothing` representa um valor ausente.

```python
from expression import Option, Some, Nothing

def get_user_name(user_id: int) -> Option[str]:
    # Simulação de busca de usuário
    if user_id == 1:
        return Some("Alice")
    else:
        return Nothing

name = get_user_name(1)  # Some("Alice")
name = get_user_name(2)  # Nothing
```

## Usando Option com Result

Option pode ser usado em conjunto com Result para representar situações onde uma operação pode falhar (retornando Error) ou retornar um valor ausente (retornando Nothing).

### Exemplo
Imagine uma função que busca um usuário no banco de dados. Ela pode falhar se houver um erro de conexão (retornando Error) ou retornar Nothing se o usuário não for encontrado.

```python
from expression import Option, Some, Nothing, Result, Ok, Error

def get_user_name(user_id: int) -> Result[Option[str], str]:
    # Simulação de busca de usuário no banco de dados
    if user_id == 1:
        return Ok(Some("Alice"))
    elif user_id == 2:
        return Ok(Nothing)  # Usuário não encontrado
    else:
        return Error("Erro de conexão com o banco de dados")

result = get_user_name(1)  # Ok(Some("Alice"))
result = get_user_name(2)  # Ok(Nothing)
result = get_user_name(3)  # Error("Erro de conexão com o banco de dados")
```

## Transformando Option com map e bind

### map
Aplica uma função a um valor Some, ou retorna Nothing se o valor for Nothing.

### bind
Similar a map, mas a função retorna outro Option. É usado para encadear operações que retornam Option.

```python
from expression import Option, Some, Nothing, option

def to_upper(name: str) -> str:
    return name.upper()

upper_name = Some("Alice").pipe(option.map(to_upper))  # Some("ALICE")
upper_name = Nothing.pipe(option.map(to_upper))  # Nothing
```

## Usando default_value e default_with

### default_value
Retorna o valor dentro de Some, ou um valor padrão se for Nothing.

### default_with
Similar a default_value, mas o valor padrão é gerado por uma função.

```python
from expression import Option, Some, Nothing

name = Some("Alice").default_value("Usuário desconhecido")  # "Alice"
name = Nothing.default_value("Usuário desconhecido")  # "Usuário desconhecido"

def get_default_name():
    return "Usuário Padrão"

name = Nothing.default_with(get_default_name)  # "Usuário Padrão"
```

## Próximos Passos

Agora você tem uma compreensão básica de Option e como ele pode ser usado em conjunto com Result. O próximo tópico abordará effect, que pode simplificar ainda mais o encadeamento de operações Result e Option.