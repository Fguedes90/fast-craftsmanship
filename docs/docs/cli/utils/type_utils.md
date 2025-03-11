# Type System

This document describes the type system utilities used in Fast Craftsmanship CLI.

## Type Safety

Fast Craftsmanship emphasizes type safety through:

- Static type annotations with mypy
- Runtime type validation
- Custom type definitions for domain concepts

## Type Utilities

The CLI provides several utilities for working with types:

### Type Validation

```python
from fcship.utils.type_utils import validate_type

# Validate at runtime
value = validate_type("test", str)  # Returns "test"
validate_type(123, str)  # Raises TypeError
```

### Custom Types

```python
from typing import NewType, List
from fcship.utils.type_utils import validate_type

# Define domain-specific types
UserId = NewType('UserId', str)
ProjectName = NewType('ProjectName', str)

# Use with validation
project_name = validate_type("my-project", ProjectName)
```

### Type Conversions

```python
from fcship.utils.type_utils import safe_cast

# Safely convert between types
int_value = safe_cast("123", int)  # Returns 123
int_value = safe_cast("not a number", int)  # Returns None
int_value = safe_cast("not a number", int, default=0)  # Returns 0
```

## Generic Programming

Fast Craftsmanship uses generics for more flexible and reusable code:

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Repository(Generic[T]):
    def __init__(self, items: List[T]):
        self.items = items
    
    def get(self, index: int) -> T:
        return self.items[index]
```

## Type Guards

Type guards are used to narrow types in a type-safe way:

```python
from typing import Union, TypeGuard
from fcship.utils.type_utils import is_string

def is_string(value: object) -> TypeGuard[str]:
    return isinstance(value, str)

def process_value(value: Union[str, int]) -> None:
    if is_string(value):
        # value is now known to be a string
        print(value.upper())
    else:
        # value is now known to be an int
        print(value + 1)
``` 