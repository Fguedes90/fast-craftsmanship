# Functional Programming

This document provides an overview of functional programming principles used in Fast Craftsmanship.

## Core Principles

Fast Craftsmanship embraces functional programming principles to create robust, maintainable code:

- **Immutability**: Prefer immutable data structures to reduce side effects
- **Pure Functions**: Functions that have no side effects and always return the same output for the same input
- **Function Composition**: Building complex behavior by combining simple functions
- **Higher-Order Functions**: Functions that take other functions as arguments or return functions
- **Type Safety**: Strong typing to catch errors at compile time

## Functional Patterns

The codebase applies several functional patterns:

- [Railway Oriented Programming (ROP)](rop.md): For error handling and flow control
- [Effects System](effects.md): For managing side effects and dependencies
- **Function Pipelines**: For data transformation workflows
- **Pattern Matching**: For expressive conditional logic

## Example

Here's a simple example of functional programming style in Fast Craftsmanship:

```python
from typing import List, Callable
from fcship.functional import pipe, map_fn, filter_fn, reduce_fn

# Define pure functions
def is_even(x: int) -> bool:
    return x % 2 == 0

def square(x: int) -> int:
    return x * x

def sum_list(nums: List[int]) -> int:
    return sum(nums)

# Compose functions with a pipeline
process_numbers = pipe(
    filter_fn(is_even),  # Keep only even numbers
    map_fn(square),      # Square each number
    sum_list             # Sum the results
)

# Apply the pipeline
result = process_numbers([1, 2, 3, 4, 5])  # Returns 20 (2² + 4² = 4 + 16 = 20)
```

## Benefits

Functional programming in Fast Craftsmanship provides:

- **Predictability**: Code behavior is more deterministic
- **Testability**: Pure functions are easier to test
- **Composability**: Small pieces can be combined in many ways
- **Parallelization**: Immutable data and pure functions enable concurrent processing
- **Reasoning**: Code is easier to reason about with reduced state and side effects

## Further Reading

- [Railway Oriented Programming (ROP)](rop.md)
- [Effects System](effects.md)
- [Functional Error Handling](../cli/utils/error_handling.md)
- [Type System](../cli/utils/type_utils.md) 