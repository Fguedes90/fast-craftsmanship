# Functional Programming with Expression

This tutorial will show you how to use the [Expression](https://github.com/dbrattli/Expression) library for functional programming in Python.

## Key Concepts

Functional programming is about programming with functions (expressions) that evaluate to values. The main concepts we'll cover:

- Pure functions - deterministic, side-effect free functions that are easier to test and reason about
- Higher-order functions - functions that take or return other functions
- Pipeline operations - composing functions in a readable way
- Immutability - using immutable data structures

## Using Expression

### Pipeline Operations

Expression provides a `pipe` function for composing operations in a readable way:

```python
from expression import pipe
from expression.collections import seq

xs = seq.range(10)

result = pipe(
        xs,
        seq.map(lambda x: x * 10),
        seq.filter(lambda x: x > 50),
        seq.fold(lambda s, x: s + x, 0),
)
```

### Currying and Partial Application 

The library supports currying functions using the `@curry` decorator:

```python
from expression import curry

@curry(1)
def add(a: int, b: int) -> int:
        return a + b

add(3)(4)  # Returns 7
```

### Collection Operations

Expression provides functional collection operations through the `seq` module:

```python
from expression.collections import seq

xs = seq.of_iterable(range(10))

mapping = seq.map(lambda x: x * 10)
filter = seq.filter(lambda x: x > 30)

result = pipe(xs,
        mapping, 
        filter,
        list,
)
```

## Best Practices

1. Use pure functions whenever possible
2. Leverage Expression's pipeline operations for readability
3. Use static type checking (Pylance in strict mode recommended)
4. Write unit tests for core business logic
5. Prefer immutable data structures
6. Keep functions small and focused
7. Use the `@curry` decorator for functions that will be used in pipelines

## Industrial Strength Code

For production-grade functional code:

- Use simple, well-tested abstractions from Expression
- Avoid mutable state and side effects
- Implement thorough unit testing
- Use static type checking
- Write clear, composable functions
- Keep your code single-threaded where possible to avoid concurrency bugs

The Expression library provides the tools needed to write robust functional code while maintaining Python's readability and simplicity.
