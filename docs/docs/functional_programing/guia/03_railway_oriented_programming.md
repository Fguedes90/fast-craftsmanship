# Railway-Oriented Programming (ROP) com Result

## O tipo Result[TSource, TError]

### O que é
Um tipo que representa o resultado de uma operação que pode ter sucesso ou falhar. `TSource` é o tipo do valor retornado em caso de sucesso, e `TError` é o tipo do valor retornado em caso de falha.

### Como ele substitui try/except
Em vez de usar try/except para capturar exceções, você retorna um Result. Isso torna o tratamento de erros explícito e parte da assinatura da função.

### Ok e Error
`Ok(value)` representa um sucesso, e `Error(error)` representa uma falha.

```python
from expression import Result, Ok, Error

def divide(a: float, b: float) -> Result[float, str]:
    if b == 0:
        return Error("Divisão por zero!")
    else:
        return Ok(a / b)

result = divide(10, 2)  # Ok(5.0)
result = divide(10, 0)  # Error("Divisão por zero!")
```

## Criando Funções que Retornam Result

### Boas práticas para ROP

- Sempre defina o tipo de erro (TError). Use strings, enums, ou classes dataclass para representar erros de forma clara.
- Evite lançar exceções dentro da função. Em vez disso, capture-as e retorne Error.
- Mantenha as funções pequenas e focadas em uma única tarefa.

### Exemplo

```python
from expression import Result, Ok, Error

def validate_email(email: str) -> Result[str, str]:
    if "@" not in email:
        return Error("Email inválido: '@' ausente")
    else:
        return Ok(email)

def send_email(email: str) -> Result[str, str]:
    # Simulação de envio de email
    if len(email) < 5:
        return Error(f"Erro ao enviar email para {email}")
    else:
        return Ok(f"Email enviado para {email}")

email_result = validate_email("test@example.com")
print(email_result)

send_result = send_email("short")
print(send_result)
```

## Manipulando Erros sem try/except

### match para inspecionar o Result

```python
from expression import Result, Ok, Error

def process_result(result: Result[int, str]):
    match result:
        case Ok(value):
            print(f"Sucesso: {value}")
        case Error(error):
            print(f"Erro: {error}")

process_result(Ok(42))
process_result(Error("Algo deu errado"))
```

### is_ok e is_error para verificação

```python
from expression import Result, Ok, Error, is_ok, is_error

result = Ok(42)

if is_ok(result):
    print("Operação bem-sucedida")

if is_error(result):
    print("Ocorreu um erro")
```

## Próximos Passos

Agora que você entende como criar e manipular Results, o próximo passo é aprender como combiná-los em pipelines. Isso é onde o ROP realmente brilha.