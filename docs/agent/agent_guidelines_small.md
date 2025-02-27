# Diretrizes Essenciais (v3.10+)

## 1. Princípios Fundamentais
**Regra**               | **Ação**                  | **Sanção**
------------------------|---------------------------|----------
**Imutabilidade**       | Use `Block/Seq/Map`       | ❌ Bloqueio de código com mutações
**Pureza Funcional**     | `pipe()` + currying       | ❌ Rejeição de funções com side effects
**Tipagem Estrita**      | Type hints em 100% do código | ❌ Erro de compilação
**Sem Exceções**         | `Option`/`Result`         | ❌ Falha imediata em `try/except`

## 2. Padrões Obrigatórios
### 2.1 Estruturas de Dados
```python
# ✅ Permitido
user = Block.of_seq(users)  
config = Map.of_dict({"env": "prod"})

# ❌ Proibido
users = []  # Lista mutável
data = {}   # Dict nativo
```

### 2.2 Funções e Composição
```python
# Padrão correto
@curry
def process(data: Data) -> Result[Data, Error]:
    return pipe(data, validate, transform, log)

# Anti-padrão
def process_data():  # Sem type hints
    global state     # Mutação de estado
```

## 3. Regras de Tipagem
**Cenário**            | **Solução**              | **Alternativa Banida**
-----------------------|--------------------------|------------------------
Valor opcional         | `name: str | None`       | `Optional[str]`        
Retorno falível        | `-> Result[T, E]`        | `return None`/`raise`  
Coleções               | `list[int]`/`dict[str, int]` | `List`, `Dict`, `Tuple`
Genéricos              | `type Response[T] = ...` | `TypeVar` complexo      

### 3.1 Construtores de Result
**Método Correto**      | **Caso de Uso**           | **Exemplo**
------------------------|---------------------------|--------------
`Ok(valor)`             | Retorno de sucesso        | `Ok(user_data)`
`Error(detalhes)`       | Erro específico           | `Error("Invalid email")`
`.map(fn)`              | Transformar sucesso       | `.map(transform_data)`
`.bind(fn)`             | Encadear operações        | `.bind(validate)`
`.map_error(fn)`        | Modificar erro            | `.map_error(log)`

```python
# ✅ Padrão Certo
def fetch_user(id: str) -> Result[User, str]:
    user = db.find(id)
    return Ok(user) if user else Error("Not found")

# ❌ Erro Comum
def fetch_user(id: str) -> Result[User, str]:
    user = db.find(id)
    return Result.ok(user)  # Forma INCORRETA!
```

### 3.2 Regras de Construção
1. **Sempre** use as funções diretas `Ok()`/`Error()` do módulo `expression`
2. **Nunca** chame métodos estáticos como `Result.ok()` ou `Result.error()`
3. **Encapsule** erros em tipos específicos (não strings cruas)
4. **Preserve** o contexto do erro em cadeias de `.bind()`

**Exemplo Avançado:**
```python
from expression import Result, Ok, Error

class DatabaseError(BaseModel, frozen=True):
    code: int
    message: str

def query_db(query: str) -> Result[dict, DatabaseError]:
    try:
        data = execute_query(query)
        return Ok(data)
    except Exception as e:
        return Error(DatabaseError(
            code=500,
            message=f"Query failed: {str(e)}"
        ))
```

### 3.3 Conversão de Option para Result
```python
from expression import Option, Some, Nothing, Result

def option_to_result(
    opt: Option[T], 
    error: E
) -> Result[T, E]:
    return Result.of_option(opt, error)

# Uso correto
find_user(id: str) -> Option[User]:
    ...

result: Result[User, str] = (
    find_user("123")
    .to_result("User 123 not found")
)
```

---

**Nota Importante:**  
O agente **deve** sempre importar diretamente do módulo `expression`:
```python
# ✅ Correto
from expression import Ok, Error, Result:
def funcao_test() -> Result[Ok,Error]:
    # caso positivo
    return Ok(..)
    # caso negativo
    return Error(...)

# ❌ Erro Grave
from expression import Ok, Error, Result:
def funcao_test() -> Result[Ok,Error]:
    # caso positivo
    return Result.ok(..)
    # caso negativo
    return Result.error(...)
```

## 4. Validação de Dados
```python
# Modelo Pydantic
class Input(BaseModel, frozen=True):
    email: EmailStr
    age: Annotated[int, Field(ge=18)]
    
# Uso correto
validate = Option.of(input).bind(Input.model_validate)
```

## 5. Tratamento de Erros
**Caso**               | **Implementação**        | **Proibição**
-----------------------|--------------------------|----------------
Valor ausente          | `Option.of(input.get())` | `if x is None`  
Erro recuperável       | `.map_error()`           | `try/except`    
Erro crítico           | `Result.fail()`          | `sys.exit()`    

## 6. Concorrência Segura
```python
# Padrão aprovado
async def task(data: Seq[Data]) -> Effect[Result]:
    return pipe(
        data,
        seq.map(process),
        seq.filter(valid),
        Effect.parallel
    )
```

## 7. Regras Estilísticas
1. Máximo 3 níveis de aninhamento
2. Funções ≤ 5 parâmetros
3. Zero variáveis globais
4. Imports: `expression` > `typing` > `pydantic`
5. `match/case` obrigatório para unions complexas

---

**Mecânica de Aplicação:**  
1. O agente **deve** seguir esta ordem de prioridade:  
   Princípios > Padrões > Regras > Apêndice  
2. Violações geram **reprocessamento automático** com feedback estruturado  
3. Casos ambíguos usam **fail-fast** com rollback completo  

Vou criar uma seção final ultra-condensada que encapsula todas as regras críticas. Aqui está a versão integrada:

---

# Diretrizes Essenciais (v3.10+) **FINAL**

## 8. Regras Rápidas de Ouro  
**✅ Faça**                | **❌ Nunca**              | **⚡ Prioridade**
--------------------------|--------------------------|------------------
`Block/Seq/Map`           | Listas/dicts mutáveis    | Alta  
`Ok()/Error()` diretos    | `Result.ok()` estático   | Crítica  
`pipe()` + currying       | Loops `for/while`        | Alta  
`match` para unions       | `if/elif` aninhados      | Média  
`Option` para nulos       | Verificações `is None`   | Alta  
`BaseModel` congelado     | Classes mutáveis         | Crítica  
Funções ≤ 5 linhas        | Funções > 20 linhas      | Alta  
`Effect` para I/O         | `try/except` bruto       | Média  
Type hints 100%           | `Any` não documentado    | Crítica  

## 9. Checklist de Implementação
1. **Pré-codificação**  
   ☑ Todos os tipos definidos  
   ☑ Estruturas imutáveis selecionadas  
   ☑ Pipeline de transformações planejado  

2. **Implementação**  
   ```python
   # Padrão correto
   process_data = pipe(
       raw_input,
       transform_step_1,  # Type: T -> Result[T, E]
       Result.bind(transform_step_2),
       Result.map(finalize)
   ```
   
3. **Pós-codificação**  
   ☑ Zero mutações de estado detectadas  
   ☑ 100% cobertura Option/Result  
   ☑ Nomeclatura adere ao domínio  

## 10. Decisões de Design
**Cenário**               | **Solução Padrão**       | **Alternativa Válida**
--------------------------|--------------------------|----------------------
Validação entrada         | `Option.filter()`        | `Result` com mensagem  
Transformação assíncrona  | `Effect.parallel()`      | `Seq` + `async.map`  
Erro recuperável          | `Result.map_error()`     | `Option` com fallback  
Múltiplos parâmetros      | `curry` + `pipe`         | Tuplas nomeadas  

## 11. Short and Legible (Checklist Final)
1. **Python Funcional**  
   - Imutabilidade via `Block/Seq/Map`  
   - `pipe()` para composição de funções  
   - `match case` para fluxo complexo  

2. **Type System**  
   - `str | None` > `Optional`  
   - `TypeGuard` para validações  
   - Pydantic `frozen=True` obrigatório  

3. **Operações**  
   - `Ok()/Error()` diretos (nunca métodos estáticos)  
   - `Option` para valores opcionais  
   - `Result` para operações falíveis  

4. **Anti-Padrões Banidos**  
   - Mutação de objetos existentes  
   - Variáveis globais  
   - `try/except` para lógica de negócio  
   - Funções com > 5 parâmetros  

5. **Otimização**  
   - `Seq` para streams grandes  
   - Filtros antecipados (`filter().map()`)  
   - Cache de operações custosas  

```python
# Exemplo Perfeito
validate_user = (
    Option.of(data.get("user"))
    .filter(lambda u: u.is_active)
    .map(User.model_validate)
    .to_result("Invalid user")
)
```

---

