---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
(tutorial_introduction)=

# Introduction to Functional Programming with Expression Library

## Core Concepts

Expression is a Python library that brings functional programming patterns to Python in a type-safe and practical way.

## Key Features

### Pure Functions

```python
# DO ✅
def add(a: int, b: int) -> int:
    return a + b

result = add(1, 2)  # Always returns 3

# DON'T ❌
total = 0
def impure_add(a: int):
    global total
    total += a
    return total

# WHY: Pure functions are predictable, testable, and thread-safe
```

### Immutable Data

```python
from expression.collections import Block, Map

# DO ✅
def process_items(items: Block[int]) -> Block[int]:
    return items.map(lambda x: x * 2)

original = Block.of_seq([1, 2, 3])
doubled = process_items(original)  # [2, 4, 6]
assert original != doubled  # Original remains unchanged

# DON'T ❌
def mutate_list(items: list) -> list:
    for i in range(len(items)):
        items[i] *= 2
    return items

# WHY: Immutability prevents accidental state changes and side effects
```

### Function Composition

```python
from expression.core import pipe

# DO ✅
def add_one(x: int) -> int: return x + 1
def double(x: int) -> int: return x * 2

result = pipe(
    5,
    add_one,    # 6
    double      # 12
)

# DON'T ❌
def process_number(x: int) -> int:
    temp = add_one(x)
    return double(temp)

# WHY: Pipe creates readable, maintainable function chains
```

### Option Type

```python
from expression import Option, Some, Nothing

# DO ✅
def divide(a: float, b: float) -> Option[float]:
    return Some(a / b) if b != 0 else Nothing

def process_division(a: float, b: float) -> str:
    return (
        divide(a, b)
        .map(lambda x: f"Result: {x}")
        .default_value("Cannot divide by zero")
    )

# DON'T ❌
def unsafe_divide(a: float, b: float) -> float | None:
    try:
        return a / b
    except ZeroDivisionError:
        return None

# WHY: Option type makes null checks explicit and composable
```

## Best Practices

### DO ✅
- Write pure functions
- Use immutable data structures
- Compose functions with pipe
- Handle null with Option
- Use type hints consistently

### DON'T ❌
- Rely on global state
- Mutate data structures
- Nest function calls deeply
- Use None for missing values
- Mix functional and imperative styles

## Practical Example

```python
from expression import Option, pipe
from expression.collections import Block
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class User:
    name: str
    age: int

def validate_age(age: int) -> Option[int]:
    return Some(age) if 0 <= age <= 120 else Nothing

def validate_name(name: str) -> Option[str]:
    return Some(name) if name.strip() else Nothing

# DO ✅
def create_user(name: str, age: int) -> Option[User]:
    return (
        validate_name(name)
        .bind(lambda n: 
            validate_age(age)
            .map(lambda a: User(n, a))
        )
    )

# Process a list of users
def process_users(data: Block[tuple[str, int]]) -> Block[User]:
    return (
        data
        .map(lambda t: create_user(*t))
        .filter_map(lambda x: x)  # Remove None values
    )

# Usage
users_data = Block.of_seq([
    ("Alice", 30),
    ("", -1),      # Invalid
    ("Bob", 25)
])

valid_users = process_users(users_data)
assert len(valid_users) == 2

# DON'T ❌
def create_user_unsafe(name: str, age: int) -> User | None:
    if not name.strip() or not (0 <= age <= 120):
        return None
    return User(name, age)

# WHY: Functional approach provides better composability and error handling
```

## Testing Example

```python
def test_user_creation():
    # Valid case
    result = create_user("Alice", 30)
    assert result.is_some()
    assert result.value.name == "Alice"
    
    # Invalid cases
    assert create_user("", 30).is_none()
    assert create_user("Bob", -1).is_none()
    
def test_user_processing():
    data = Block.of_seq([
        ("Alice", 30),
        ("", -1),
        ("Bob", 25)
    ])
    
    result = process_users(data)
    assert len(result) == 2
    assert all(isinstance(u, User) for u in result)
