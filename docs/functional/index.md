# Functional Programming in Fast Craftsmanship

Fast Craftsmanship is built on functional programming principles, particularly Railway Oriented Programming (ROP), to create robust, maintainable, and testable code.

## Why Functional Programming?

Functional programming provides several benefits for a CLI tool like Fast Craftsmanship:

- **Error Handling**: Explicit error paths with `Result` types
- **Composability**: Functions can be easily combined and reused
- **Testability**: Pure functions are easier to test
- **Predictability**: Reduced side effects lead to more predictable code
- **Readability**: Clear data flow and transformation pipelines

## Core Concepts

### Railway Oriented Programming (ROP)

Railway Oriented Programming is a functional approach to handling errors and composing functions. It uses a `Result` type to represent either a successful outcome or an error.

```python
from expression import Result, Ok, Error

def divide(a: int, b: int) -> Result[float, str]:
    if b == 0:
        return Error("Cannot divide by zero")
    return Ok(a / b)
```

### Function Composition

Functions can be composed together using pipelines:

```python
from expression import pipe, pipeline

def process_data(data: str) -> Result[str, str]:
    return pipeline(
        validate,
        transform,
        save
    )(data)
```

### Effect Functions

For sequential operations where each step depends on the previous one, we use effect functions:

```python
from expression import effect

@effect.result[str, str]()
def process_user(user_id: str):
    user = yield from fetch_user(user_id)
    profile = yield from get_profile(user)
    settings = yield from load_settings(profile)
    return settings
```

## Core Types

Fast Craftsmanship uses these core functional types:

### Result

`Result[T, E]` represents either a successful value of type `T` or an error of type `E`:

```python
from expression import Result, Ok, Error

result = divide(10, 2)  # Ok(5.0)
result = divide(10, 0)  # Error("Cannot divide by zero")

# Pattern matching
match result:
    case Ok(value):
        print(f"Success: {value}")
    case Error(msg):
        print(f"Error: {msg}")
```

### Option

`Option[T]` represents either a value of type `T` or the absence of a value:

```python
from expression import Option, Some, Nothing

option = find_user("alice")  # Some(User(...))
option = find_user("unknown")  # Nothing

# Pattern matching
match option:
    case Some(user):
        print(f"Found user: {user.name}")
    case Nothing:
        print("User not found")
```

### Tagged Union

`Tagged Union` allows creating custom union types with multiple cases:

```python
from expression import tagged_union, tag
from typing import Literal

@tagged_union
class ApiError:
    tag: Literal["validation", "network", "server"] = tag()
    
    validation: str = case()
    network: str = case()
    server: int = case()
```

## Best Practices

When working with Fast Craftsmanship, follow these functional programming best practices:

1. **Use Result for Error Handling**: Avoid exceptions and use `Result` types
2. **Compose Functions**: Use pipelines to build complex operations
3. **Keep Functions Pure**: Minimize side effects and make them explicit
4. **Make Data Immutable**: Use immutable data structures (like Pydantic models)
5. **Pattern Match**: Use pattern matching to handle different cases

## Learn More

- [Railway Oriented Programming](rop.md) - Learn about the ROP pattern
- [Effect Functions](effects.md) - Understand effect functions in depth