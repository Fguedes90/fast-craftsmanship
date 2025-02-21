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
(tutorial_lambda_calculus)=

# Lambda Calculus

Lambda calculus was introduced by mathematician Alonzo Church in the 1930s as part of an
investigation into the foundations of mathematics

- Lambda calculus is a formal language
- The expressions of the language are called lambda terms
- Everything is a function, there are no literals

In lambda calculus, we write `(f x)` instead of the more traditional `f(x)`.

Many real-world programming languages can be regarded as extensions of the lambda
calculus. This is true for all functional programming languages, a class that includes
Lisp, Scheme, Haskell, and ML (OCaml, F#).


# Lambda Calculus in Python with Expression Library

## Core Concepts

Lambda calculus forms the foundation of functional programming. The Expression library provides tools to work with lambda functions effectively.

## Basic Lambda Functions

```python
from expression.core import curry, compose, pipe
from typing import Callable

# DO ✅
# Simple, focused lambda functions with descriptive names
add_numbers = lambda x, y: x + y
double_number = lambda x: x * 2
check_even = lambda x: x % 2 == 0

# Curried functions for partial application
@curry
def multiply(x: int, y: int) -> int:
    return x * y

double_nums = multiply(2)  # Creates a new function
assert double_nums(4) == 8

# DON'T ❌
# Complex, multi-purpose lambdas
complex_lambda = lambda x, y: (x * 2 if isinstance(x, int) else str(x)) + y

# WHY: Simple lambdas are easier to understand and compose
```

## Function Composition

```python
# DO ✅
# Compose functions clearly
increment_number = lambda x: x + 1

# Using pipe
result = pipe(
    5,
    increment_number,  # 6
    double_number,     # 12
    str               # "12"
)

# Using compose
number_to_str = compose(str, double_number, increment_number)
assert number_to_str(5) == "12"

# DON'T ❌
# Nested function calls
def process_number(x):
    return str(double(increment(x)))

# WHY: Composition makes data flow explicit and readable
```

## Higher-Order Functions

```python
from expression.collections import Block

# DO ✅
def create_validator(min_val: int, max_val: int) -> Callable[[int], bool]:
    return lambda x: min_val <= x <= max_val

is_adult = create_validator(18, 120)
assert is_adult(25) == True
assert is_adult(15) == False

# Filter with composed predicates
check_not = lambda pred: lambda x: not pred(x)

numbers = Block.of_seq(range(10))
evens = numbers.filter(check_even)
odds = numbers.filter(check_not(check_even))

# DON'T ❌
def validate_age(age: int) -> bool:
    if age < 18:
        return False
    if age > 120:
        return False
    return True

# WHY: Higher-order functions enable flexible, reusable logic
```

## Practical Patterns

### Function Factories

```python
# DO ✅
def create_formatter(prefix: str) -> Callable[[str], str]:
    return lambda text: f"{prefix}: {text}"

log_error = create_formatter("ERROR")
log_info = create_formatter("INFO")

assert log_error("Failed") == "ERROR: Failed"
assert log_info("Success") == "INFO: Success"

# DON'T ❌
class Logger:
    def __init__(self, prefix):
        self.prefix = prefix
    
    def log(self, text):
        return f"{self.prefix}: {text}"

# WHY: Function factories are simpler and more functional
```

### Function Composition with Types

```python
from typing import TypeVar, Callable

T = TypeVar('T')
U = TypeVar('U')
V = TypeVar('V')

# DO ✅
def compose2(g: Callable[[U], V], 
            f: Callable[[T], U]) -> Callable[[T], V]:
    return lambda x: g(f(x))

# Type-safe transformation chain
parse_int = lambda s: int(s)
is_positive = lambda n: n > 0
validate_number = compose2(is_positive, parse_int)

assert validate_number("42") == True
assert validate_number("-1") == False

# DON'T ❌
def validate_number_unsafe(s: str) -> bool:
    try:
        return int(s) > 0
    except ValueError:
        return False

# WHY: Typed composition ensures type safety
```

## Best Practices

### DO ✅
- Write small, focused lambda functions
- Use curry for partial application
- Compose functions with pipe or compose
- Create function factories for reusable logic
- Use type hints with lambda functions

### DON'T ❌
- Write complex lambda expressions
- Mix lambda and regular functions inconsistently
- Nest function calls deeply
- Create stateful closures
- Ignore type safety in compositions

## Testing Example

```python
def test_function_composition():
    # Given
    increment = lambda x: x + 1
    multiply_by_two = lambda x: x * 2
    convert_to_string = lambda x: str(x)
    
    # When
    composed = compose(convert_to_string, multiply_by_two, increment)
    piped = lambda x: pipe(x, increment, multiply_by_two, convert_to_string)
    
    # Then
    assert composed(5) == "12"
    assert piped(5) == "12"

def test_higher_order_function():
    # Given
    is_valid_age = create_validator(18, 120)
    
    # Then
    assert is_valid_age(25) == True
    assert is_valid_age(15) == False
    assert is_valid_age(150) == False
