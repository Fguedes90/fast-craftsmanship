# Padrões e Boas Práticas para ROP com expression

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

Lembre-se de que a chave é isolar os efeitos colaterais, usar dados imutáveis e compor funções Result em pipelines claros e concisos.