# Modelagem de Dados Imutáveis para ROP

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
- Use Static Factories para criar instâncias de seus tipos `tagged_union` de forma controlada.