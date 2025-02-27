# Fundamentos do Functional Programming e expression para ROP

## Pure Functions

### O que são
Funções que sempre retornam o mesmo resultado para as mesmas entradas e não têm efeitos colaterais (não modificam estado externo).

### Por que são importantes para ROP
Facilitam o raciocínio sobre o código e tornam os pipelines mais previsíveis. Se uma função é pura, você pode ter certeza de que ela só fará o que está explicitamente definido, sem causar surpresas.

### Exemplo

```python
def add(a: int, b: int) -> int:  # Pura
    return a + b

total = 0
def impure_add(a: int) -> int:  # Impura (modifica estado externo)
    global total
    total += a
    return total
```

## Immutability

### O que é
Dados que não podem ser modificados após a criação.

### Por que é importante para ROP
Evita bugs causados por mutação inesperada. Com dados imutáveis, você pode ter certeza de que o valor que você está usando não será alterado por outra parte do código.

### Como usar com expression
Use `dataclass(frozen=True)` para criar classes imutáveis.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    x: int
    y: int

p1 = Point(1, 2)
# p1.x = 3  # Isso causaria um erro (dataclass é imutável)
p2 = Point(3, 4) # Cria um novo objeto, não modifica o existente
```

## Higher-Order Functions

### O que são
Funções que recebem outras funções como argumentos ou retornam funções.

### Por que são importantes para ROP
Permitem abstrair padrões de comportamento e criar código mais reutilizável. `map`, `filter`, `fold` são exemplos clássicos.

### Exemplo

```python
def apply_operation(func, value):
    return func(value)

def square(x):
    return x * x

result = apply_operation(square, 5) # square é uma higher-order function
```

## Instalação e Configuração

### Instalação

```bash
pip install expression
```

### Importando

```python
from expression import pipe, Result, Ok, Error
from expression.extra import result
from dataclasses import dataclass
from typing import Literal
from expression import case, tag, tagged_union
from expression import curry
from expression import effect, Option, Some, Nothing
```

## expression para ROP - Visão Geral

- A biblioteca expression fornece as ferramentas para aplicar os conceitos acima de forma prática.
- O tipo Result é o coração do ROP, permitindo representar sucesso ou falha de uma operação.
- As funções pipe e pipeline permitem encadear operações Result de forma legível e segura.
- O objetivo é substituir try/except, loops e if/else por construções funcionais que são mais fáceis de testar e manter.# Modelagem de Dados com Pydantic 2.0+ para ROP

## Introdução

Pydantic 2.0+ oferece uma maneira robusta e performática de modelar dados com validação em tempo de execução, perfeitamente adequada para uso com Railway-Oriented Programming (ROP).

## Instalação

```bash
pip install "pydantic>=2.0"
```

## Modelo Base Imutável

Primeiro, vamos criar um modelo base que todas as nossas classes podem herdar, garantindo imutabilidade por padrão:

```python
from pydantic import BaseModel, ConfigDict
from typing import TypeVar, Type
from expression import Result, Ok, Error

T = TypeVar('T', bound='ImmutableModel')

class ImmutableModel(BaseModel):
    """Modelo base imutável para todos os modelos Pydantic."""
    model_config = ConfigDict(frozen=True)
    
    @classmethod
    def create(cls: Type[T], **data) -> Result[T, str]:
        """
        Factory method que retorna um Result contendo o modelo ou erro.
        
        Exemplo:
            result = User.create(name="Alice", email="alice@example.com")
            match result:
                case Ok(user):
                    print(f"Usuário criado: {user.name}")
                case Error(msg):
                    print(f"Erro: {msg}")
        """
        try:
            instance = cls(**data)
            return Ok(instance)
        except Exception as e:
            return Error(str(e))
```

## Usando o Modelo Base

### Modelos Simples

```python
from datetime import datetime
from typing import List, Optional

class User(ImmutableModel):
    id: int
    name: str
    email: str
    created_at: datetime
    tags: List[str] = []
    profile_url: Optional[str] = None

# Criando uma instância usando o factory method
result = User.create(
    id=1,
    name="Alice",
    email="alice@example.com",
    created_at=datetime.now(),
    tags=["admin"]
)

# O modelo é imutável por padrão
# user.name = "Bob"  # Raises FrozenInstanceError
```

### Modelos com Validadores

```python
from pydantic import EmailStr, model_validator
from decimal import Decimal

class Order(ImmutableModel):
    items: List[str]
    total: Decimal
    customer_email: EmailStr
    
    @model_validator(mode='after')
    def validate_total(self) -> 'Order':
        if len(self.items) == 0 and self.total > 0:
            raise ValueError("Cannot have total > 0 with no items")
        return self

# O método create já lida com os erros de validação
result = Order.create(
    items=["item1", "item2"],
    total=Decimal("100.50"),
    customer_email="customer@example.com"
)
```

## Composição de Modelos

```python
class Address(ImmutableModel):
    street: str
    city: str
    country: str

class Item(ImmutableModel):
    name: str
    price: Decimal
    quantity: int

class CompleteOrder(ImmutableModel):
    id: int
    customer: User
    shipping_address: Address
    items: List[Item]
    
    @property
    def total(self) -> Decimal:
        return sum(item.price * item.quantity for item in self.items)
```

## Pipeline ROP com Modelos Imutáveis

```python
from expression import pipeline
from typing import Dict, Any

def validate_order_data(data: Dict[Any, Any]) -> Result[CompleteOrder, str]:
    return CompleteOrder.create(**data)

def process_order(order: CompleteOrder) -> Result[str, str]:
    if order.total > 1000:
        return Error("Ordem excede limite máximo")
    return Ok(f"Ordem processada: {order.id}")

def send_confirmation(message: str) -> Result[str, str]:
    return Ok(f"Confirmação enviada: {message}")

# Pipeline completo
order_pipeline = pipeline(
    validate_order_data,
    process_order,
    send_confirmation
)

# Exemplo de uso
order_data = {
    "id": 1,
    "customer": {
        "id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "created_at": datetime.now()
    },
    "shipping_address": {
        "street": "Rua Principal",
        "city": "São Paulo",
        "country": "Brasil"
    },
    "items": [
        {"name": "Item 1", "price": Decimal("100.00"), "quantity": 2},
        {"name": "Item 2", "price": Decimal("50.00"), "quantity": 1}
    ]
}

result = order_pipeline(order_data)
```

## Melhores Práticas

1. **Use o Modelo Base**
   - Herde de `ImmutableModel` para todos os seus modelos
   - Utilize o método `create` para instanciar modelos de forma segura
   - Aproveite o tratamento de erros embutido

2. **Validação Rigorosa**
   - Adicione validadores customizados quando necessário
   - Use tipos específicos do Pydantic (EmailStr, HttpUrl, etc.)
   - Mantenha as validações no nível do modelo

3. **Composição de Modelos**
   - Use modelos aninhados para estruturas complexas
   - Mantenha a imutabilidade em todos os níveis
   - Aproveite as properties para cálculos derivados

4. **Integração com ROP**
   - Use o método `create` em conjunto com pipeline
   - Mantenha a consistência no tratamento de erros
   - Combine validações do Pydantic com lógica de negócios

## Exemplo de Uso Avançado

```python
from datetime import date
from typing import Dict, Any

class AgeValidator(ImmutableModel):
    birth_date: date
    
    @model_validator(mode='after')
    def validate_age(self) -> 'AgeValidator':
        today = date.today()
        age = (
            today.year - self.birth_date.year -
            ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )
        if age < 18:
            raise ValueError("Must be at least 18 years old")
        return self

class AdvancedUser(ImmutableModel):
    name: str
    email: EmailStr
    birth_date: date
    preferences: Dict[str, Any]
    
    @model_validator(mode='after')
    def validate_user(self) -> 'AdvancedUser':
        # Valida idade usando o validador dedicado
        AgeValidator(birth_date=self.birth_date)
        return self

# O método create lida com todas as validações
result = AdvancedUser.create(
    name="Alice",
    email="alice@example.com",
    birth_date=date(1990, 1, 1),
    preferences={"theme": "dark", "notifications": True}
)
```

Esta abordagem com um modelo base imutável simplifica a criação de modelos, garante consistência e reduz a duplicação de código em todo o projeto.# Modelagem de Dados Imutáveis para ROP

## dataclass para Dados Imutáveis Simples

### O que é
Uma forma concisa de criar classes que automaticamente geram métodos como `__init__`, `__repr__`, `__eq__`, etc. Quando usado com `frozen=True`, torna a classe imutável.

### Por que é importante para ROP
Garante que os dados que você está passando pelos seus pipelines não serão alterados inesperadamente.

### Exemplo

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str

user = User(id=1, name="Alice", email="alice@example.com")
# user.email = "new_email@example.com"  # Isso causaria um erro
```

## tagged_union para Modelar Tipos Complexos

### O que é
Uma forma de definir um tipo que pode ser um de vários tipos diferentes, cada um com seus próprios dados. É como um enum esteroidado. Fornece type safety superior a unions regulares.

### Por que é importante para ROP
Permite representar diferentes estados ou resultados possíveis de uma operação de forma clara e segura. É especialmente útil para modelar erros.

### Exemplo

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from expression import case, tag, tagged_union

@tagged_union
class OperationResult:
    tag: Literal["success", "failure"] = tag()

    success: str = case()
    failure: str = case()

    @staticmethod
    def Success(message: str) -> OperationResult:
        return OperationResult(success=message)

    @staticmethod
    def Failure(error: str) -> OperationResult:
        return OperationResult(failure=error)

result = OperationResult.Success("Operação concluída com sucesso!")
# result = OperationResult(failure="Erro ao processar") # Isso causaria um erro
```

## Static Factories

### O que são
Métodos estáticos dentro de uma classe que são usados para criar instâncias dessa classe.

### Por que são importantes para ROP
Permitem controlar a criação de objetos e garantir que eles sejam sempre criados em um estado válido. Com `tagged_union`, eles são a forma recomendada de criar instâncias.

### Exemplo (já visto no tagged_union)

```python
@staticmethod
def Success(message: str) -> OperationResult:
    return OperationResult(success=message)

@staticmethod
def Failure(error: str) -> OperationResult:
    return OperationResult(failure=error)
```

## Como isso se encaixa no ROP

- Use `dataclass` para modelar os dados que suas funções ROP processam.
- Use `tagged_union` para modelar os resultados de suas operações, especialmente para representar sucesso e diferentes tipos de falha.
- Use Static Factories para criar instâncias de seus tipos `tagged_union` de forma controlada.# Railway-Oriented Programming (ROP) com Result

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

Agora que você entende como criar e manipular Results, o próximo passo é aprender como combiná-los em pipelines. Isso é onde o ROP realmente brilha.# Composição Funcional com pipe e pipeline

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

Agora você tem as ferramentas essenciais para ROP: Result, pipe e pipeline. O próximo tópico abordará Option, que pode ser útil em cenários específicos onde você precisa lidar com a ausência de valores além dos erros representados por Result.# Gerenciando Valores Opcionais com Option

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

Agora você tem uma compreensão básica de Option e como ele pode ser usado em conjunto com Result. O próximo tópico abordará effect, que pode simplificar ainda mais o encadeamento de operações Result e Option.# Efeitos com effect

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

Agora você tem uma compreensão de como usar `@effect.result` e `@effect.option` para simplificar o encadeamento de operações. O próximo tópico abordará Try, que é uma forma simplificada de Result quando você está lidando principalmente com exceções.# Try: Simplificando Result com Exceções

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
   - Você está construindo uma API que outros desenvolvedores usarão# Padrões e Boas Práticas para ROP com expression

## Lidar com I/O de Forma Funcional

### O Desafio
I/O (entrada/saída) é inerentemente impuro (tem efeitos colaterais). Como lidar com isso em um estilo funcional?

### A Solução
Isolar os efeitos colaterais o máximo possível. Empurre a lógica impura para as bordas do seu sistema e mantenha o núcleo o mais puro possível.

### Padrões

#### Funções que retornam Result para I/O
Envolva chamadas de I/O em funções que retornam Result. Capture exceções e retorne Error.

#### Injeção de Dependência
Passe as dependências de I/O como argumentos para suas funções, em vez de codificá-las diretamente. Isso torna suas funções mais testáveis e flexíveis.

### Exemplo

```python
import os
from expression import Result, Ok, Error

def read_file(filename: str) -> Result[str, str]:
    try:
        with open(filename, "r") as f:
            return Ok(f.read())
    except FileNotFoundError:
        return Error(f"Arquivo não encontrado: {filename}")
    except Exception as ex:
        return Error(f"Erro ao ler arquivo: {ex}")

def write_file(filename: str, content: str) -> Result[None, str]:
    try:
        with open(filename, "w") as f:
            f.write(content)
        return Ok(None)
    except Exception as ex:
        return Error(f"Erro ao escrever arquivo: {ex}")
```

## Testes Unitários para Código Funcional

### O Objetivo
Testar pipelines de Result para garantir que eles se comportem como esperado em diferentes cenários (sucesso, falha, diferentes tipos de erros).

### Estratégias

1. **Testar Funções Individuais**: Teste cada função que retorna Result individualmente para garantir que ela retorne os valores corretos para diferentes entradas.

2. **Testar Pipelines**: Teste os pipelines completos para garantir que eles lidem com erros corretamente e produzam os resultados esperados.

3. **Usar Asserções para Ok e Error**: Use asserções para verificar se um Result é Ok ou Error e para verificar o valor dentro do Result.

### Exemplo (usando pytest)

```python
import pytest
from expression import Ok, Error, is_ok, is_error
from your_module import validate_age, grant_access, access_pipeline

def test_validate_age_valid():
    result = validate_age(25)
    assert is_ok(result)
    assert result.value == 25

def test_validate_age_invalid():
    result = validate_age(-5)
    assert is_error(result)
    assert result.error == "Idade inválida"

def test_access_pipeline_success():
    result = access_pipeline(25)
    assert is_ok(result)
    assert result.value == "Acesso concedido"

def test_access_pipeline_failure():
    result = access_pipeline(-5)
    assert is_error(result)
    assert result.error == "Idade inválida"
```

## Evitando Efeitos Colaterais

### O Objetivo
Manter o código o mais puro possível para facilitar o raciocínio e o teste.

### Estratégias

1. **Não Modificar Estado Global**: Evite modificar variáveis globais ou estado compartilhado.

2. **Não Fazer I/O Diretamente**: Envolva chamadas de I/O em funções que retornam Result e injete as dependências de I/O.

3. **Usar Dados Imutáveis**: Use `dataclass(frozen=True)` e `tagged_union` para garantir que os dados não sejam modificados inesperadamente.

## Usando Type Hints

### O Objetivo
Aumentar a segurança e a clareza do código.

### Como
Use type hints em todas as funções e variáveis. Isso ajuda a detectar erros em tempo de desenvolvimento e torna o código mais fácil de entender.

### Exemplo

```python
from expression import Result

def validate_email(email: str) -> Result[str, str]:
    if "@" not in email:
        return Error("Email inválido")
    return Ok(email)
```

## Conclusão

Ao seguir estes padrões e boas práticas, você criará código mais:
- Testável
- Manutenível
- Previsível
- Seguro contra erros
- Fácil de entender e raciocinar sobre

Lembre-se de que a chave é isolar os efeitos colaterais, usar dados imutáveis e compor funções Result em pipelines claros e concisos.# Concorrência e Paralelismo com ROP e expression

## O Desafio da Concorrência

- Concorrência (múltiplas tarefas parecem executar ao mesmo tempo) e paralelismo (múltiplas tarefas realmente executam ao mesmo tempo) introduzem complexidade devido a potenciais condições de corrida, deadlocks e outros problemas.
- O estado mutável compartilhado é a principal fonte desses problemas.

## Princípios Funcionais para Concorrência

### Imutabilidade
Use dados imutáveis para evitar condições de corrida. Se os dados não podem ser modificados, não há risco de múltiplas threads/processos tentarem modificá-los simultaneamente.

### Isolamento de Efeitos Colaterais
Mantenha as operações que interagem com o mundo externo (I/O, estado mutável) o mais isoladas possível.

### Funções Puras
Use funções puras sempre que possível. Funções puras são thread-safe por natureza, pois não dependem de estado externo.

## Abordagens com expression e ROP

### MailboxProcessor (Concorrência)

MailboxProcessor é um ator (actor) assíncrono que permite enviar e receber mensagens entre diferentes partes do seu programa. Ele encapsula o estado e a lógica de processamento em um único lugar, evitando a necessidade de bloqueios (locks) e outras primitivas de sincronização.

#### Como usar com ROP
O MailboxProcessor pode receber mensagens que contêm dados e funções a serem executadas. Essas funções podem retornar Result, permitindo que você aplique os princípios do ROP dentro do ator.

#### Exemplo

```python
import asyncio
from expression import MailboxProcessor, Ok, Error

async def worker(inbox):
    while True:
        msg = await inbox.receive()
        if msg == "quit":
            break
        try:
            result = process_data(msg)  # process_data retorna Result
            print(f"Worker recebeu: {msg}, Resultado: {result}")
        except Exception as ex:
            print(f"Worker recebeu: {msg}, Erro: {ex}")

async def main():
    inbox = MailboxProcessor(worker)
    asyncio.create_task(inbox.start())

    await inbox.post("data1")
    await inbox.post("data2")
    await inbox.post("quit")

asyncio.run(main())
```

### asyncio e Funções Assíncronas (Concorrência)

asyncio permite escrever código concorrente usando async e await.

#### Como usar com ROP
Crie funções assíncronas que retornam Result. Use await para desempacotar os Results e propague os erros usando pipeline ou @effect.result.

#### Exemplo

```python
import asyncio
from expression import Result, Ok, Error, pipeline

async def fetch_data(url: str) -> Result[str, str]:
    # Simulação de chamada de rede
    await asyncio.sleep(1)
    if "example" in url:
        return Ok(f"Dados de {url}")
    else:
        return Error(f"Falha ao buscar dados de {url}")

async def process_data(data: str) -> Result[str, str]:
    # Simulação de processamento
    await asyncio.sleep(0.5)
    return Ok(data.upper())

async def main():
    fetch_and_process = pipeline(
        fetch_data,
        process_data
    )

    result1 = await fetch_and_process("http://example.com")
    result2 = await fetch_and_process("http://invalid.com")

    print(result1)
    print(result2)

asyncio.run(main())
```

### multiprocessing (Paralelismo)

multiprocessing permite executar código em múltiplos processos, aproveitando múltiplos núcleos de CPU.

#### Como usar com ROP
Divida o trabalho em tarefas independentes que podem ser executadas em paralelo. Cada tarefa deve receber dados imutáveis como entrada e retornar um Result. Use uma fila (queue) para coletar os resultados e tratar os erros.

#### Importante
A comunicação entre processos geralmente envolve serialização/desserialização, então certifique-se de que seus tipos Result e os dados que eles contêm sejam serializáveis.

#### Exemplo

```python
import multiprocessing
from expression import Result, Ok, Error
import time

def process_item(item: int) -> Result[int, str]:
    """Simula uma tarefa que pode ter sucesso ou falhar."""
    time.sleep(0.1)  # Simula trabalho
    if item % 2 == 0:
        return Ok(item * 2)
    else:
        return Error(f"Erro ao processar item: {item}")

def main():
    items = list(range(10))
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(process_item, items)

    successful_results = []
    errors = []
    for result in results:
        if isinstance(result, Ok):  # Usando isinstance para compatibilidade com multiprocessing
            successful_results.append(result.value)
        elif isinstance(result, Error):
            errors.append(result.error)

    print("Resultados de sucesso:", successful_results)
    print("Erros:", errors)

if __name__ == "__main__":
    main()
```

## Padrões Avançados

### Error Aggregation
Em cenários concorrentes, você pode querer coletar todos os erros, em vez de interromper no primeiro erro. Isso pode ser feito usando `asyncio.gather` ou `multiprocessing.Pool` e combinando os resultados em uma lista de Results.

### Circuit Breaker
Para evitar sobrecarregar serviços remotos, implemente um padrão de "circuit breaker". Se um serviço falhar repetidamente, interrompa as chamadas até que ele se recupere.

## Boas Práticas

1. **Comece Simples**: Evite concorrência/paralelismo a menos que seja realmente necessário.

2. **Priorize Imutabilidade**: Use dados imutáveis sempre que possível.

3. **Teste Exaustivamente**: Teste seu código concorrente/paralelo em diferentes condições para garantir que ele seja robusto.

4. **Monitore**: Monitore o desempenho do seu código concorrente/paralelo para identificar gargalos e problemas.

5. **Serialização**: Ao usar multiprocessing, certifique-se de que os dados que você está passando para os processos filhos são serializáveis. Tipos complexos podem precisar de tratamento especial.