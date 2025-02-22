# Agent Guidelines

Este documento contém as diretrizes obrigatórias para que o agente LLM produza código conforme os padrões e regras da nossa documentação. Devido à limitação de contexto, as informações são concisas e objetivas. Sempre siga o método único estabelecido para cada situação, utilizando as funções e classes utilitárias especificadas.

## ⚠️ Requisitos e Avisos

- Utilize apenas recursos disponíveis no **Python 3.10 ou superior**:
  - Pattern matching estrutural com `match`/`case`
  - Union types com operador `|` (ex: `str | None` em vez de `Optional[str]`)
  - Type guards com `TypeGuard`
  - Parâmetros e retornos tipados para funções
  - Type aliases com `type` (PEP 695)
  - Generic type aliases (ex: `type JsonDict[T] = dict[str, T]`)

- Evite o uso de recursos depreciados, como:
  - Type hints da biblioteca `typing` que já existem nativamente (ex: `List`, `Dict`, `Tuple`) (use `list`, `dict`, `tuple` em vez disso)
  - `Callable` e `Awaitable` do módulo `typing` (use `collections.abc` em vez disso)
  - Uso de `TypeVar` quando puder usar PEP 695 (`type Foo[T] = ...`)
  - Sintaxe antiga do Pydantic (v1.x)
  - Tipagem com `Any` sem necessidade explícita

## 1. Princípios Fundamentais

### 1.1. Imutabilidade
- **DO's:**
  - Utilize **Block** para coleções pequenas ou médias, criando-as com `Block.of_seq(...)`
  - Utilize **Seq** para processamento lazy de grandes conjuntos ou fluxos infinitos
  - Utilize **Map** para dicionários, criados com `Map.of_seq(...)`
  - Use `BaseModel` do Pydantic com `frozen=True` para estruturas de dados imutáveis
  - Utilize métodos que retornam novas instâncias

- **DON'Ts:**
  - Não modifique estruturas de dados existentes
  - Não use listas, dicionários ou sets mutáveis do Python
  - Não armazene estado em variáveis globais
  - Não misture estruturas mutáveis e imutáveis

**Exemplo:**
```python
from expression.collections import Block, Map, seq

numbers = Block.of_seq(range(10))
config = Map.of_seq([("host", "localhost"), ("port", 5432)])
large_stream = seq(range(1_000_000))
```

### 1.2. Funções Puras e Composição
- **DO's:**
  - Todas as funções devem ser puras, sem efeitos colaterais
  - Use `pipe` para encadeamento claro de operações
  - Documente tipos de parâmetros com type hints
  - Use currying para aplicação parcial de funções
  - Mantenha funções pequenas e focadas

 - **DON'Ts:**
   - Não crie funções com efeitos colaterais
   - Não use exceções para controle de fluxo
   - Não misture estilos funcional e imperativo
   - Não crie currying profundamente aninhado

### 1.3. Tratamento de Valores Opcionais
- **DO's:**
  - Use `Option` para valores que podem estar ausentes
  - Use `match()` para tratamento consistente de casos Some/None
  - Encadeie transformações com `.bind()` e `.map()`
  - Retorne cedo com `Option.none()`
  - Use `default_value()` para valores padrão
  - Documente retornos Option

- **DON'Ts:**
  - Não acesse `.value` diretamente
  - Não misture com verificações de None
  - Não ignore casos None
  - Não levante exceções
  - Não use para tratamento de erros
  - Não aninhe Options profundamente

**Exemplos:**
```python
from expression import Option, Some, Nothing
from typing import Any

def get_key(d: Option[dict], k: str) -> Option[Any]:
    """Acessa uma chave do dicionário de forma segura."""
    return d.bind(lambda x: Option.of_obj(x.get(k)))

def get_nested(data: dict, *keys: str) -> Option[Any]:
    """Acessa chaves aninhadas de forma segura."""
    return functools.reduce(get_key, keys, Option.some(data))

def is_valid_age(age: int) -> bool:
    """Verifica se a idade está no intervalo válido."""
    return 0 <= age <= 150

def validate_email(email: str) -> Option[str]:
    """Valida formato do email."""
    return Option.some(email) if "@" in email else Option.none()

def validate_age(age: int) -> Option[int]:
    """Valida idade."""
    return Option.some(age) if is_valid_age(age) else Option.none()

def create_user(name: str, email: str, age: int) -> User:
    """Cria instância de usuário."""
    return User(name=name, email=email, age=age)

def validate_user_data(data: dict) -> Option[User]:
    """Valida dados do usuário."""
    return (Option.of_obj(data.get("name"))
            .filter(bool)
            .bind(lambda name:
                  Option.of_obj(data.get("email"))
                  .bind(validate_email)
                  .bind(lambda email:
                        Option.of_obj(data.get("age"))
                        .bind(validate_age)
                        .map(lambda age: create_user(name, email, age)))))

def first_matching[T](pred: Callable[[T], bool], xs: Iterable[T]) -> Option[T]:
    """Encontra primeiro item que atende ao predicado."""
    return next(
        (Option.some(x) for x in xs if pred(x)), 
        Option.none()
    )
```

**Exemplo:**
```python
from expression import pipe, curry

@curry
def transform_data(value: str) -> str:
    """Transforma dados de entrada."""
    return value.upper()

@curry
def validate_data(value: str) -> bool:
    """Valida dados transformados."""
    return len(value) > 0

def format_output(value: str) -> str:
    """Formata saída de dados."""
    return f"Processed: {value}"

def process_data(data: str) -> str:
    """Processa dados através de pipeline."""
    return pipe(
        data,
        transform_data,
        validate_data,
        format_output
    )
```

## 2. Tratamento de Erros e Efeitos

### 2.1. Railway-Oriented Programming
- **DO's:**
  - Use **Result** para operações que podem falhar
  - Encadeie operações com `.bind()` e transforme com `.map()`
  - Trate erros explicitamente com `.map_error()`
  - Crie validadores especializados usando currying
  - Use `catch_errors` para converter exceções em Result

- **DON'Ts:**
  - Não use try/except para lógica de negócio
  - Não retorne None para indicar falha
  - Não misture Result com exceções
  - Não ignore erros em operações que podem falhar

**Exemplos:**
```python
from expression import Result, Ok, Error, Option, Some, Nothing, union
from typing import List
from typing_extensions import Annotated
from pydantic import BaseModel, EmailStr, Field, field_validator

class ValidationError(BaseModel):
    """Base para erros de validação."""
    field: str
    message: str

    model_config = {
        "frozen": True
    }

class ValidationErrors(BaseModel):
    """Coleção de erros de validação."""
    errors: list[ValidationError] = []

    model_config = {
        "frozen": True
    }

class UserData(BaseModel):
    """Modelo de dados do usuário com validação."""
    name: Annotated[str, Field(min_length=1, max_length=100)]
    email: EmailStr
    age: Annotated[int, Field(ge=0, le=150)]

    model_config = {
        "frozen": True
    }

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validação adicional de campos."""
        errors = []
        
        if not values.name:
            errors.append(ValidationError(field="name", message="Name is required"))
        elif len(values.name) > 100:
            errors.append(ValidationError(field="name", message="Name too long"))
            
        if errors:
            return ValidationErrors(errors=errors)
        return values

def validate_form(data: dict) -> Result[UserData, ValidationErrors]:
    """Valida formulário usando Pydantic."""
    try:
        user = UserData.model_validate(data)
        return Ok(user)
    except ValueError as e:
        errors = [ValidationError(field=err["loc"][0], message=err["msg"])
                 for err in e.errors()]
        return Error(ValidationErrors(errors=errors))

def find_user(id: str) -> Option[dict]:
    """Busca usuário por ID."""
    users = {"1": {"name": "Alice"}}
    return Some(users[id]) if id in users else Nothing

def find_and_validate(id: str) -> Result[UserData, str]:
    """Busca e valida usuário."""
    return (find_user(id)
            .to_result(f"User {id} not found")
            .bind(lambda user: validate_form(user))
            .map_error(lambda errs: "; ".join(f"{e.field}: {e.message}" for e in errs.errors)))
```

### 2.2. Efeitos e Operações Assíncronas
- **DO's:**
  - Use **Effect** para operações com efeitos colaterais
  - Utilize `.bind()` e `.map()` para encadear efeitos
  - Converta para async com `.to_awaitable()`
  - Cache resultados de operações custosas
  - Use `Effect.success/fail` para resultados claros
  - Implemente tratamento de erros com `.catch()`

- **DON'Ts:**
  - Não misture Effect com try/except
  - Não execute I/O sem Effect
  - Não ignore falhas em operações assíncronas
  - Não bloqueie o event loop
  - Não retorne None ou strings de erro
  - Não misture Effect com tipos Optional
  - Não aninhe efeitos desnecessariamente

**Exemplo:**
```python
from expression import Effect

async def fetch_data(url: str) -> Effect[str]:
    """Busca dados de uma URL."""
    return Effect.success(await http_client.get(url))

async def process_response(data: str) -> Effect[str]:
    """Processa resposta HTTP."""
    return Effect.success(data.upper())

async def handle_request(url: str) -> Effect[str]:
    """Manipula requisição HTTP."""
    return (await fetch_data(url)
            .bind(process_response)
            .catch(lambda e: Effect.success("Fallback value"))
    ).to_awaitable()
```

## 3. Modelagem de Dados

### 3.1. Modelos Pydantic Imutáveis
- **DO's:**
  - Use `BaseModel` com `frozen=True` para tipos de valor imutáveis
  - Defina validadores de campo com `Field`
  - Use `model_validator` para validação complexa
  - Implemente validação customizada quando necessário
  - Use `EmailStr`, `HttpUrl` e outros tipos especializados
  - Use enums do Pydantic para tipos enumerados

- **DON'Ts:**
  - Não use classes mutáveis
  - Não misture diferentes abordagens de validação
  - Não ignore validações do Pydantic
  - Não misture dados e comportamento
  - Não modifique estado interno
  - Não use strings para discriminação de tipos

**Exemplos:**
```python
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Literal
from enum import Enum

class UserRole(str, Enum):
    """Roles disponíveis para usuários."""
    ADMIN = "admin"
    USER = "user"

class Email(BaseModel):
    """Representa um endereço de email válido."""
    value: EmailStr

    model_config = {
        "frozen": True
    }

class UserProfile(BaseModel):
    """Perfil do usuário com dados validados."""
    email: Email
    name: Annotated[str, Field(min_length=1, max_length=100)]
    role: Annotated[UserRole, Field(default=UserRole.USER)]
    website: Annotated[HttpUrl | None, Field(default=None)]

    model_config = {
        "frozen": True
    }

    @property
    def is_admin(self) -> bool:
        """Verifica se usuário é admin."""
        return self.role == UserRole.ADMIN
```

### 3.2. Tagged Unions
- **DO's:**
  - Use `@tagged_union` para tipos soma
  - Forneça métodos estáticos para cada variante
  - Use `match()` para pattern matching exaustivo
  - Documente cada variante
  - Implemente tagged unions genéricos quando apropriado

- **DON'Ts:**
  - Não use enums ou strings para estados
  - Não misture unions com herança
  - Não deixe casos sem tratamento no match
  - Não adicione métodos de instância

## 4. Programação Concorrente

### 4.1. Message Passing
- **DO's:**
  - Use `mailbox()` para comunicação entre threads
  - Implemente timeouts em operações bloqueantes
  - Utilize mailboxes com limites (`max_size`)
  - Documente protocolos de mensagens
  - Monitore tamanhos de filas
  - Implemente tratamento de backpressure

- **DON'Ts:**
  - Não compartilhe estado mutável
  - Não bloqueie indefinidamente
  - Não misture com locks/mutexes
  - Não ignore capacidade das filas
  - Não passe objetos complexos
  - Não deixe recursos abertos

**Exemplo:**
```python
from expression import mailbox, Result, Ok
from collections.abc import Callable\2
from functools import reduce

T = TypeVar('T')

def process_message[T](msg: T, handler: Callable[[T], Result[T, str]]) -> Result[T, str]:
    """Processa uma mensagem individual."""
    return handler(msg)

def process_messages[T](msgs: Iterable[T], handler: Callable[[T], Result[T, str]]) -> Result[List[T], str]:
    """Processa múltiplas mensagens."""
    return reduce(
        lambda acc, msg: acc.bind(lambda xs: 
            process_message(msg, handler).map(lambda x: xs + [x])),
        msgs,
        Ok([])
    )

def create_worker_pool(size: int) -> tuple[Mailbox, Mailbox]:
    """Cria pool de workers com mailboxes limitados."""
    tasks = mailbox(max_size=100)
    results = mailbox(max_size=100)
    for _ in range(size):
        spawn_worker(tasks, results)
    return tasks, results

def spawn_worker(tasks: Mailbox[T], results: Mailbox[Result[T, str]]) -> None:
    """Inicia worker em nova thread."""
    Thread(target=worker_loop, args=(tasks, results)).start()

def worker_loop[T](tasks: Mailbox[T], results: Mailbox[Result[T, str]]) -> None:
    """Loop principal do worker usando recursão."""
    def process_next() -> None:
        task = tasks.receive()
        if not task.is_stop():
            result = process_message(task, process_task)
            results.post(result)
            process_next()
    
    process_next()
```

## 5. Depuração e Performance

### 5.1. Ferramentas de Debug
- **DO's:**
  - Use `debug()` para inspeção temporária
  - Profile gargalos de performance
  - Cache computações custosas
  - Monitore padrões de uso de memória
  - Implemente debug type-safe
  - Documente ferramentas de debug

- **DON'Ts:**
  - Não deixe chamadas de debug em produção
  - Não ignore vazamentos de memória
  - Não faça cache de dados voláteis
  - Não misture código de debug/produção
  - Não crie efeitos colaterais no debug
  - Não use print para debug

### 5.2. Otimização
- **DO's:**
  - Use `Seq` para grandes conjuntos
  - Aplique filtros o mais cedo possível
  - Cache operações custosas
  - Monitore uso de memória
  - Use operações em lote quando possível

- **DON'Ts:**
  - Não avalie sequências desnecessariamente
  - Não crie listas intermediárias grandes
  - Não ignore profiling
  - Não negligencie limpeza de cache

## 7. Utilitários e Funções Auxiliares

### 7.1. Manipulação de Arquivos e Tipos
- **DO's:**
  - Use `ensure_directory(path)` para garantir existência de diretórios
  - Use `create_files(files, base_path)` para criar múltiplos arquivos
  - Use `ensure_type(value, type_constructor, type_name, validation_fn)` para validação de tipos
  - Use `map_type(f, type_constructor)` para transformações tipadas

- **DON'Ts:**
  - Não crie diretórios/arquivos manualmente
  - Não faça validações de tipo ad-hoc
  - Não misture diferentes estilos de validação
  - Não ignore erros de validação de tipos

**Exemplo:**
```python
from fcship.utils.file_utils import ensure_directory, create_files
from fcship.utils.type_utils import ensure_type, map_type
from pathlib import Path
from pydantic import BaseModel, Field
from typing_extensions import Annotated

class FileContent(BaseModel):
    """Modelo para conteúdo de arquivo."""
    path: Annotated[Path, Field()]
    content: Annotated[str, Field()]

    model_config = {
        "frozen": True
    }

def setup_project_structure(base_path: Path) -> None:
    """Configura estrutura inicial do projeto."""
    ensure_directory(base_path)
    
    files = [
        FileContent(path=base_path / "config.json", content="{}"),
        FileContent(path=base_path / "README.md", content="# Project")
    ]
    
    for file in files:
        create_files({file.path.name: file.content}, file.path.parent)

def process_integer(value: str) -> int:
    """Processa string para inteiro com validação."""
    def is_valid_integer(s: str) -> bool:
        return s.isdigit()
    
    return ensure_type(value, int, "integer", is_valid_integer)
```

### 7.2. Utilitários Funcionais
- **DO's:**
  - Use `lift_option(fn)` para elevar Option para Result
  - Use `collect_results(results)` para agregar resultados assíncronos
  - Use `tap(fn)` e `tap_async(fn)` para efeitos colaterais seguros
  - Use `handle_command_errors(fn)` para tratamento de erros em comandos

- **DON'Ts:**
  - Não misture diferentes padrões de tratamento de erros
  - Não ignore falhas em operações assíncronas
  - Não execute efeitos colaterais diretamente
  - Não trate erros de forma ad-hoc

**Exemplo:**
```python
from fcship.utils.functional import lift_option, tap
from fcship.utils.error_handling import handle_command_errors
from pydantic import BaseModel

class CommandResult(BaseModel):
    """Resultado de execução de comando."""
    success: Annotated[bool, Field()]
    message: Annotated[str, Field()]

    model_config = {
        "frozen": True
    }

def find_user(id: str) -> Option[dict]:
    """Busca usuário no banco de dados."""
    return Option.of_obj(users.get(id))

@lift_option
def get_user(id: str) -> Option[dict]:
    """Busca usuário com elevação automática para Result."""
    return find_user(id)

def create_log_entry(message: str) -> CommandResult:
    """Cria entrada de log."""
    return CommandResult(success=True, message=message)

def process_data(data: str) -> Result[CommandResult, str]:
    """Processa dados com logging seguro."""
    log_entry = create_log_entry(f"Processing: {data}")
    return (Ok(data)
            .map(tap(lambda _: log_entry))
            .bind(process_data)
            .map(tap(lambda _: create_log_entry(f"Complete: {data}"))))

@handle_command_errors
def execute_operation(operation: str, name: str) -> None:
    """Executa operação com tratamento de erros."""
    def validate_operation(op: str, name: str) -> None:
        if op not in valid_operations:
            raise ValueError(f"Invalid operation: {op}")
    
    validate_operation(operation, name)
```

## 6. Estilo e Legibilidade

### 6.1. Princípios de Clareza
- **DO's:**
  - Quebre funções grandes em funções pequenas e reutilizáveis
  - Use funções nomeadas em vez de lambdas inline
  - Mantenha tipagem explícita com type hints
  - Encadeie operações de forma clara com `pipe()`, `map()`, `filter()`
  - Centralize transformações de dados no início do fluxo
  - Seja consistente com a nomenclatura de funções e variáveis
  - Documente transformações complexas claramente
  - Use pattern matching para dados complexos
  - Use recursão em vez de loops imperativos quando apropriado

- **DON'Ts:**
  - Não declare lambdas aninhadas
  - Não passe lambdas como argumentos diretos
  - Não use loops imperativos (for/while)
  - Não dependa de estados globais
  - Não misture estilos imperativos e funcionais
  - Não escreva funções com múltiplas responsabilidades

**Exemplo de Código Legível:**
```python
def is_valid(x: int) -> bool:
    """Verifica se valor está no intervalo válido."""
    return 0 < x < 100

def double(x: int) -> int:
    """Dobra o valor de entrada."""
    return x * 2

def format_result(x: int) -> str:
    """Formata resultado para exibição."""
    return f"Result: {x}"

def process_value(input_value: int) -> str:
    """Processa valor através de pipeline de transformações."""
    return pipe(input_value, is_valid, double, format_result)
```

# Short and Legible
1️⃣ **Evite mutações de estado.** Retorne novos valores em vez de modificar variáveis existentes.  
2️⃣ **Quebre funções grandes.** Divida lógica complexa em funções pequenas e reutilizáveis.  
3️⃣ **Use funções nomeadas.** Evite lambdas inline em favor de funções nomeadas para maior clareza.  
4️⃣ **Mantenha a tipagem explícita.** Use anotações de tipo para facilitar a leitura e evitar erros.  
5️⃣ **Encadeie operações de forma clara.** Use `bind()`, `pipe()`, `map()`, `filter()` e `reduce()` para evitar aninhamento.  
6️⃣ **Faça código idempotente.** Garanta que funções sempre retornem o mesmo resultado para os mesmos argumentos.  
7️⃣ **Evite efeitos colaterais.** Não altere variáveis externas ou estados globais.  
8️⃣ **Priorize a imutabilidade.** Use estruturas de dados imutáveis sempre que possível.  
9️⃣ **Escreva testes pequenos e focados.** Teste funções isoladas, cobrindo diferentes cenários.  
🔟 **Prefira a simplicidade.** Escreva código claro e direto, evitando truques complicados.  
1️⃣1️⃣ **Trate erros de forma explícita.** Use tipos como `Result` ou `Option` para representar falhas.  
1️⃣2️⃣ **Evite loops imperativos.** Substitua `for` e `while` por funções como `map()`, `filter()` e `reduce()`.  
1️⃣3️⃣ **Use recursão quando apropriado.** Prefira recursão em vez de loops mutáveis.  
1️⃣4️⃣ **Implemente padrões funcionais.** Aplique currying, composição e funções puras.  
1️⃣5️⃣ **Centralize a transformação de dados.** Realize transformações no início do fluxo de dados.  
1️⃣6️⃣ **Evite dependência de estados globais.** Mantenha o estado controlado e limitado.  
1️⃣7️⃣ **Seja consistente com a nomenclatura.** Use nomes claros e consistentes para funções e variáveis.  
1️⃣8️⃣ **Use pattern matching.** Utilize correspondência de padrões para manipular dados complexos.  
1️⃣9️⃣ **Controle os efeitos colaterais.** Realize efeitos colaterais no final do fluxo de dados.  
2️⃣0️⃣ **Documente transformações complexas.** Explique funções e transformações complexas claramente.  
2️⃣1️⃣ **Nunca declare funções lambdas aninhadas ou como argumento para outras funções.** Sempre atribua lambdas a variáveis e use essas variáveis nas funções.


## Referências

Para mais informações sobre os assuntos abordados neste documento, consulte:

- [Introdução à Programação Funcional](docs/docs/functional_programing/tutorial/introduction.md)
- [Tutorial de Containers](docs/docs/functional_programing/tutorial/containers.md)
- [Tutorial de Efeitos](docs/docs/functional_programing/tutorial/effects.md)
- [Ferramentas de Debug](docs/docs/functional_programing/reference/debugging.md)
- [Referências - Block, Map, Option, Result](docs/docs/functional_programing/reference/)
