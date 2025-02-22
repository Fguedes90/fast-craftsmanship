# Funções Utilitárias

Esta seção documenta as funções utilitárias presentes no projeto, que auxiliam em diversas tarefas comuns, tais como manipulação de arquivos, validação de tipos, composição funcional e tratamento de erros. Essas funções fazem parte dos módulos:
- `fcship/fcship/utils/file_utils.py`
- `fcship/fcship/utils/type_utils.py`
- `fcship/fcship/utils/functional.py`
- `fcship/fcship/utils/error_handling.py`

## 1. Utilitários de Arquivos

As funções presentes em `fcship/fcship/utils/file_utils.py` auxiliam na manipulação de arquivos e diretórios.

**Principais funções:**
- **`ensure_directory(path: Path)`**  
  Garante que o diretório pai do caminho fornecido exista, criando-o se necessário.

- **`file_creation_status(title: str)`**  
  Fornece um contexto para rastrear e exibir o status de criação de arquivos.

- **`create_files(files: dict[str, str], base_path: str = "")`**  
  Cria múltiplos arquivos a partir de um dicionário que mapeia caminhos para conteúdos.

**Exemplo de Uso:**

```python
from pathlib import Path
from .fcship.utils.file_utils import ensure_directory, create_files

# Garante que o diretório exista
ensure_directory(Path("/caminho/para/arq.txt"))

# Criação de múltiplos arquivos
files = {
    "arquivo1.txt": "Conteúdo do arquivo 1",
    "arquivo2.txt": "Conteúdo do arquivo 2",
}
create_files(files, base_path="/output")
```

## 2. Utilitários de Tipos

As funções do módulo `fcship/fcship/utils/type_utils.py` garantem a conversão e validação de tipos.

**Principais funções:**
- **`ensure_type(value, type_constructor, type_name, validation_fn)`**  
  Converte e valida um valor para o tipo desejado; se a validação falhar, gera um erro.

- **`map_type(f, type_constructor)`**  
  Aplica uma função de transformação em um valor (convertido para string) e reconstrói o tipo original.

**Exemplo de Uso:**

```python
from .fcship.utils.type_utils import ensure_type, map_type
from expression import Ok

# Valida e converte um valor para inteiro
value = "123"
converted_value = ensure_type(value, int, "int", lambda x: x.isdigit())
print(converted_value)  # 123

# Transforma um valor mantendo sua tipagem
transform = lambda s: Ok(s.strip().upper())
mapper = map_type(transform, str)
result = mapper(" abc ")
print(result.ok)  # "ABC"
```

## 3. Utilitários Funcionais

O módulo `fcship/fcship/utils/functional.py` reúne funções para composição funcional e gerenciamento de efeitos colaterais.

**Principais funções:**
- **`lift_option(fn)`**  
  Eleva uma função que retorna um `Option` para uma função que retorna um `Result`.

- **`collect_results(results)`**  
  Agrupa vários resultados assíncronos, short-circuitando em caso de erro.

- **`tap(fn)` e `tap_async(fn)`**  
  Permitem executar efeitos colaterais (como logging) dentro de cadeias de transformações sem alterar o valor.

**Exemplo de Uso:**

```python
from .fcship.utils.functional import lift_option, tap

def get_optional_value(key: str):
    from expression import Option
    value = {"chave": "valor"}.get(key)
    return Option.of_obj(value)

# Eleva a função que retorna Option para Result
lifted = lift_option(get_optional_value)
result = lifted("chave")
print(result.ok)  # "valor"

# Utilizando tap para executar um log sem alterar o valor
v = tap(lambda x: print("Valor recebido:", x))("teste")
print(v)  # "teste"
```

## 4. Utilitários de Tratamento de Erros

O módulo `fcship/fcship/utils/error_handling.py` fornece ferramentas para capturar e tratar erros de forma funcional.

**Principais funções:**
- **`handle_command_errors(fn)`**  
  Decorador que captura erros em funções de comando, exibindo mensagens apropriadas e realizando o encerramento controlado da aplicação.

- **`validate_operation(...)`**  
  Realiza a validação de operações e argumentos, lançando exceções quando os parâmetros necessários não são fornecidos.

**Exemplo de Uso:**

```python
import typer
from .fcship.utils.error_handling import handle_command_errors, validate_operation

@handle_command_errors
def executar_comando(operation: str, name: str | None = None) -> None:
    valid_operations = ["create", "update", "delete"]
    validate_operation(operation, valid_operations, name, requires_name=["update", "delete"])
    typer.echo(f"Operação {operation} executada com sucesso!")

# Executa o comando, exibindo erro se os parâmetros forem inválidos.
executar_comando("create")
```

## Considerações Finais

As funções utilitárias contribuem para um design funcional e modular, promovendo a reutilização de código, imutabilidade e tratamento explícito de erros. Ao utilizá-las, asseguramos que operações comuns sejam realizadas de maneira consistente e previsível, facilitando a manutenção e evolução do sistema.
