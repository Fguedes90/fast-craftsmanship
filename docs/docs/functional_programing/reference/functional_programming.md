# Functional Programming with Expression Library

## Overview
This guide covers functional programming concepts and their practical implementation using the Expression library, from theoretical foundations to real-world patterns.

## Core Concepts

### Lambda Calculus Foundations
Lambda calculus, introduced by Alonzo Church in the 1930s, forms the theoretical basis of functional programming. Key concepts:
- Everything is a function
- Functions are first-class values
- Functions can be composed
- Pure functions have no side effects

### Currying and Partial Application
```python
from expression import curry

# Basic currying
@curry
def add(x: int, y: int) -> int:
    return x + y

add_one = add(1)      # Partial application
assert add_one(2) == 3
assert add(1)(2) == 3  # Full currying

# Multiple argument currying
@curry
def transform(f, g, x):
    return f(g(x))

double = lambda x: x * 2
inc = lambda x: x + 1
inc_then_double = transform(double)(inc)
assert inc_then_double(3) == 8  # (3 + 1) * 2
```

### Function Composition
```python
from expression.core import pipe, compose

# Using pipe for left-to-right composition
result = pipe(
    5,
    lambda x: x + 1,  # 6
    lambda x: x * 2,  # 12
    str               # "12"
)

# Using compose for right-to-left composition
number_to_str = compose(
    str,
    lambda x: x * 2,
    lambda x: x + 1
)
assert number_to_str(5) == "12"
```

## Functional Patterns

### Pure Functions and Immutability
```python
from dataclasses import dataclass
from expression.collections import Block

@dataclass(frozen=True)  # Immutable data structure
class Score:
    value: int
    subject: str

def calculate_average(scores: Block[Score]) -> float:
    return scores.map(lambda s: s.value).average()

def filter_high_scores(scores: Block[Score]) -> Block[Score]:
    return scores.filter(lambda s: s.value >= 90)
```

### Higher-Order Functions
```python
from typing import TypeVar, Callable
from expression import Option, Some, Nothing

T = TypeVar('T')
U = TypeVar('U')

def safe_transform(f: Callable[[T], U]) -> Callable[[T], Option[U]]:
    """Creates a safe version of a function that might fail."""
    def wrapper(x: T) -> Option[U]:
        try:
            return Some(f(x))
        except Exception:
            return Nothing
    return wrapper

# Usage
safe_int = safe_transform(int)
assert safe_int("123").value == 123
assert safe_int("abc").is_none()
```

### Function Factories
```python
@curry
def filter_by(pred, xs):
    """Creates specialized filter functions."""
    return [x for x in xs if pred(x)]

is_even = lambda x: x % 2 == 0
filter_evens = filter_by(is_even)
assert filter_evens([1,2,3,4]) == [2,4]

# Data transformation factories
@curry
def map_field(field: str, f, d: dict) -> dict:
    """Creates specialized dictionary field transformers."""
    return {**d, field: f(d.get(field))}

to_upper = lambda s: s.upper() if s else s
uppercase_name = map_field('name', to_upper)
data = {'name': 'alice', 'age': 25}
assert uppercase_name(data)['name'] == 'ALICE'
```

## Advanced Patterns

### Railway-Oriented Programming
```python
from expression import Result

def validate_field(field: str, pred, data: dict) -> Result[dict, str]:
    """Validates a dictionary field using a predicate."""
    value = data.get(field)
    return (Result.ok(data) if pred(value)
            else Result.error(f"Invalid {field}: {value}"))

# Create specialized validators
@curry
def validate(pred, error, x):
    return Result.ok(x) if pred(x) else Result.error(error)

is_string = lambda x: isinstance(x, str)
not_empty = lambda x: bool(x and x.strip())

validate_string = validate(is_string)("Must be string")
validate_not_empty = validate(not_empty)("Must not be empty")

def validate_name(name):
    return (Result.ok(name)
            | validate_string
            | validate_not_empty)
```

### Type-Safe Composition
```python
from typing import TypeVar, Callable

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

@curry
def compose2[T, U, V](g: Callable[[U], V],
                      f: Callable[[T], U]) -> Callable[[T], V]:
    """Type-safe function composition."""
    return lambda x: g(f(x))

# Usage with types
def parse(s: str) -> int:
    return int(s)

def double(x: int) -> int:
    return x * 2

safe_double = compose2(double, parse)
assert safe_double("21") == 42
```

## Best Practices

### DO ✓
- Use frozen dataclasses for data structures
- Write small, focused pure functions
- Compose functions with pipe and compose
- Use curry for partial application
- Handle errors with Option and Result
- Use type hints consistently
- Create function factories for reusable logic
- Document parameter order in curried functions

### DON'T ✗
- Mutate data structures
- Write functions with side effects
- Mix functional and imperative styles
- Create complex class hierarchies
- Over-complicate simple operations
- Ignore parameter types
- Create deeply nested curries
- Use exceptions for control flow

## Testing Patterns

### Unit Testing
```python
def test_curry():
    @curry
    def add3(x, y, z):
        return x + y + z
    
    add1_and = add3(1)
    add1_2_and = add1_and(2)
    
    assert add1_2_and(3) == 6
    assert add3(1)(2)(3) == 6

def test_function_composition():
    increment = lambda x: x + 1
    double = lambda x: x * 2
    to_str = lambda x: str(x)
    
    composed = compose(to_str, double, increment)
    piped = lambda x: pipe(x, increment, double, to_str)
    
    assert composed(5) == "12"
    assert piped(5) == "12"
```

### Property Testing
```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.integers(), st.integers())
def test_curry_properties(x: int, y: int):
    """Test that curried and uncurried forms are equivalent."""
    @curry
    def add2(a: int, b: int) -> int:
        return a + b
    
    assert add2(x)(y) == add2(x, y)

@given(st.lists(st.integers()))
def test_composition_properties(xs: list[int]):
    """Test that composition preserves function properties."""
    double = lambda x: x * 2
    increment = lambda x: x + 1
    
    # Test composition associativity
    f1 = compose(double, increment)
    f2 = lambda x: double(increment(x))
    
    assert all(f1(x) == f2(x) for x in xs)
```

## Performance Considerations

1. Function Creation
   - Each curry creates new function objects
   - Cache partially applied functions
   - Consider stack depth for deep currying

2. Composition Overhead
   - Minimal runtime overhead per function
   - Use uncurried form for tight loops
   - Chain operations efficiently

3. Data Structure Impact
   - Immutable operations create new instances
   - Use appropriate data structures (Block, Map, Seq)
   - Consider memory usage patterns

4. Optimization Tips
   - Profile complex function chains
   - Cache expensive computations
   - Use bulk operations when possible
   - Consider evaluation order