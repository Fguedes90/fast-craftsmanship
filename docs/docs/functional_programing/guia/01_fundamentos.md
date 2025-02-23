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
- O objetivo é substituir try/except, loops e if/else por construções funcionais que são mais fáceis de testar e manter.