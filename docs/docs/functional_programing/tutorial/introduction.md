# Introduction to Functional Programming with Expression Library

## Why Expression?

Expression brings practical functional programming to Python by providing:
- Type-safe operations without exceptions
- Immutable data structures
- Composable functions and pipelines
- Railway-oriented programming patterns
- Thread-safe concurrency primitives

## Getting Started

### Installation
```python
# Basic installation
pip install expression

# With Pydantic support
pip install expression[pydantic]
```

## Core Concepts

### 1. Pure Functions
Functions that:
- Always produce the same output for the same input
- Have no side effects
- Don't modify external state

```python
# Pure function
def add(x: int, y: int) -> int:
    return x + y

# Impure function (avoid)
total = 0
def add_to_total(x: int) -> int:
    global total
    total += x
    return total
```

### 2. Immutable Data
Data that cannot be changed after creation:
```python
from expression.collections import Block, Map

# Immutable list
numbers = Block.of(1, 2, 3)
more_numbers = numbers.cons(0)  # Creates new Block: [0,1,2,3]

# Immutable dictionary
scores = Map.of_seq([("Alice", 90), ("Bob", 85)])
new_scores = scores.add("Charlie", 95)  # Creates new Map
```

### 3. Railway-Oriented Programming
Handle success/failure paths explicitly:
```python
from expression import Result, Ok, Error

def divide(x: float, y: float) -> Result[float, str]:
    return Ok(x / y) if y != 0 else Error("Division by zero")

def process_division(x: float, y: float) -> str:
    return (divide(x, y)
        .map(lambda result: f"Result: {result}")
        .match(
            lambda value: value,
            lambda error: f"Error: {error}"
        ))
```

### 4. Option Type
Handle optional values safely:
```python
from expression import Option, Some, Nothing

def find_user(user_id: str) -> Option[dict]:
    return Some({"id": user_id, "name": "Test"}) if user_id else Nothing

def greet_user(user_id: str) -> str:
    return (find_user(user_id)
        .map(lambda user: f"Hello, {user['name']}")
        .match(
            lambda msg: msg,
            lambda: "User not found"
        ))
```

## Best Practices

1. Prefer Immutability
   - Use Block instead of list
   - Use Map instead of dict
   - Create new instances instead of modifying

2. Handle Errors Explicitly
   - Use Result for operations that can fail
   - Use Option for optional values
   - Never throw/catch exceptions in business logic

3. Compose Functions
   - Use pipe and compose for clear data flow
   - Chain operations with method chaining
   - Keep functions small and focused

4. Type Safety First
   - Use type hints consistently
   - Let Result/Option handle special cases
   - Validate data at boundaries

## Common Patterns

### Data Validation
```python
def validate_user(data: dict) -> Result[dict, str]:
    return (Result.ok(data)
        .bind(validate_required_fields)
        .bind(validate_field_types)
        .bind(validate_business_rules))
```

### Data Transformation
```python
def transform_data(items: Block[dict]) -> Block[Result[dict, str]]:
    return (items
        .map(validate_item)    # Validate each
        .map(transform_item)   # Transform valid
        .filter(lambda r: r.is_ok()))  # Keep successes
```

### Safe Resource Handling
```python
def process_file(path: str) -> Result[dict, str]:
    return (Try.catch(lambda: open(path).read())
        .map(str.strip)
        .bind(parse_json)
        .map_error(str))
```

## Integration with Python Ecosystem

### With Pydantic
```python
from pydantic import BaseModel
from expression import Result

class User(BaseModel):
    name: str
    age: int

def create_user(data: dict) -> Result[User, str]:
    try:
        return Result.ok(User(**data))
    except Exception as e:
        return Result.error(str(e))
```

### With Async/Await
```python
async def fetch_user(id: str) -> Result[User, str]:
    try:
        response = await http_client.get(f"/users/{id}")
        return Result.ok(User(**response.json()))
    except Exception as e:
        return Result.error(str(e))
```

## Testing Guide

### Unit Testing
```python
def test_validation():
    # Test success case
    result = validate_user({"name": "Alice", "age": 30})
    assert result.is_ok()
    assert result.ok["name"] == "Alice"

    # Test failure case
    result = validate_user({"name": "", "age": -1})
    assert result.is_error()
    assert "Invalid age" in result.error

### Property Testing
```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.integers())
def test_option_properties(x: int):
    opt = Some(x)
    # Identity
    assert opt.map(lambda x: x) == opt
    # Composition
    f = lambda x: x * 2
    g = lambda x: x + 1
    assert (opt.map(f).map(g) == 
            opt.map(lambda x: g(f(x))))
```

## Performance Considerations

1. Lazy Evaluation
   - Use Seq for large datasets
   - Chain operations before evaluation
   - Use early filtering

2. Memory Usage
   - Block and Map share structure
   - Release references when done
   - Consider batch processing

3. CPU Optimization
   - Use appropriate data structures
   - Minimize transformations
   - Profile critical paths

