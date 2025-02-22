# Pipe

## Overview
Pipe enables functional programming data flow by chaining operations left-to-right using either the pipe function or the `|` operator. It provides a more readable alternative to nested function calls and enables clear transformation pipelines.

## When to Use
✓ Complex data transformations
✓ Function composition chains
✓ Data processing workflows
✓ Functional programming patterns
✓ Readable transformation chains

## When Not to Use
✗ Simple single transformations
✗ Heavy imperative logic needed
✗ Complex branching required
✗ Performance-critical loops

## Core Operations

### Basic Pipe (Function Style)
```python
from expression import pipe
result = pipe(
    "Hello World",     # Initial value
    str.lower,         # Transform to lowercase
    str.split,         # Split into words
    list              # Convert to list
)
assert result == ["hello", "world"]
```

### Pipeline Style (Operator)
```python
from expression import pipe
result = (
    "Hello World"  # Initial value
    | str.lower    # Transform to lowercase
    | str.split    # Split into words
    | list         # Convert to list
)
assert result == ["hello", "world"]
```

### Pipe with Lambdas
```python
numbers = pipe(
    range(10),
    lambda xs: filter(lambda x: x % 2 == 0, xs),  # Keep evens
    lambda xs: map(lambda x: x * 2, xs),          # Double
    list
)
assert numbers == [0, 4, 8, 12, 16]
```

## Common Patterns

### Data Transformation
```python
def process_data(raw: str) -> Result[dict, str]:
    return pipe(
        raw,
        str.strip,                # Clean input
        parse_json,               # Parse to dict
        validate_schema,          # Validate structure
        transform_data            # Transform content
    )
```

### Option Chain
```python
from expression import Option

def safe_process(data: str) -> Option[int]:
    return pipe(
        data,
        safe_parse_int,          # Try parse to int
        lambda x: x.filter(is_valid),  # Validate
        lambda x: x.map(transform)     # Transform if valid
    )
```

### Result Chain
```python
from expression import Result

def validate_input(data: dict) -> Result[dict, str]:
    return pipe(
        Result.ok(data),
        lambda r: r.bind(validate_required),  # Check required
        lambda r: r.bind(validate_types),     # Check types
        lambda r: r.bind(validate_rules)      # Check rules
    )
```

## Best Practices

### DO ✓
- Keep transformations focused
- Use clear lambda names
- Handle errors explicitly
- Document complex chains
- Type hint where possible

### DON'T ✗
- Create overly long chains
- Mix unrelated operations
- Hide side effects
- Ignore error cases
- Nest pipes deeply

## Integration Examples

### With Standard Library
```python
from functools import partial
from operator import add, mul

# Point-free arithmetic
add_one = partial(add, 1)
double = partial(mul, 2)
result = pipe(
    3,
    double,      # 3 * 2 = 6
    add_one      # 6 + 1 = 7
)
assert result == 7
```

### With Collections
```python
from expression.collections import Block

def process_numbers(data: list[str]) -> int:
    return pipe(
        data,
        Block.of_seq,           # Create Block
        lambda xs: xs.filter(bool),  # Remove empty
        lambda xs: xs.map(int),      # Convert to ints
        lambda xs: xs.sum()          # Sum values
    )

data = ["1", "2", "", "3"]
assert process_numbers(data) == 6
```

### With Option/Result
```python
def safe_computation(x: str) -> Option[float]:
    return pipe(
        x,
        safe_parse_float,         # Parse to float
        lambda o: o.bind(safe_sqrt),  # Try sqrt
        lambda o: o.filter(is_valid)  # Validate
    )
```

## Type Safety

### Function Signatures
```python
from typing import Callable, TypeVar

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

def compose2[A, B, C](g: Callable[[B], C], 
                      f: Callable[[A], B]) -> Callable[[A], C]:
    """Compose two functions with type safety."""
    return lambda x: g(f(x))

# Usage with types
def parse(s: str) -> int:
    return int(s)

def double(x: int) -> int:
    return x * 2

safe_double = compose2(double, parse)
assert safe_double("21") == 42
```

### Type Parameters
```python
from typing import TypeVar, Callable

T = TypeVar('T')
R = TypeVar('R')

def transform[T, R](data: T, f: Callable[[T], R]) -> R:
    return pipe(
        data,
        f,
        validate_result[R]
    )
```

## Common Use Cases

### API Processing
```python
def process_api_response(response: Response) -> Result[dict, str]:
    return pipe(
        response,
        lambda r: r.text,            # Get text
        parse_json,                  # Parse JSON
        validate_response,           # Validate
        transform_response           # Transform
    )
```

### Data Validation
```python
def validate_user_data(data: dict) -> Result[User, list[str]]:
    return pipe(
        data,
        validate_required_fields,    # Check required
        validate_field_types,        # Check types
        validate_business_rules,     # Check rules
        create_user                  # Create if valid
    )
```

### Configuration Loading
```python
def load_config(path: str) -> Result[Config, str]:
    return pipe(
        path,
        read_file,                  # Read file
        parse_yaml,                 # Parse YAML
        validate_config,            # Validate
        create_config               # Create config
    )
```

## Performance Notes

1. Each step creates new value
2. Chain operations efficiently
3. Handle early termination
4. Consider evaluation order
5. Profile complex chains
6. Minimal overhead per function call
7. Consider function call stack depth
8. Use standard functions for simple cases

## Testing Examples

### Unit Tests
```python
def test_pipe_transformation():
    result = pipe(
        "42",
        int,              # Parse string
        lambda x: x * 2,  # Double
        str              # Convert back
    )
    assert result == "84"
```

### Property Tests
```python
@given(st.integers())
def test_pipe_properties(x: int):
    # Identity
    assert pipe(x, lambda y: y) == x
    
    # Composition
    f = lambda x: x * 2
    g = lambda x: x + 1
    
    assert pipe(x, f, g) == pipe(x, lambda y: g(f(y)))
```

### Integration Tests
```python
def test_data_pipeline():
    data = {"name": "test", "age": "25"}
    
    result = pipe(
        data,
        validate_input,      # Returns Result
        lambda r: r.bind(transform_data),
        lambda r: r.map(create_user)
    )
    
    assert result.is_ok()
    assert isinstance(result.value, User)