# Effects and Expression

This guide focuses on using the `expression` library to handle effects in Python, specifically using Options.

## Effects

Effects are values with a context. The context varies depending on the effect type.  `expression` provides tools to work with these wrapped values safely.

Examples of effects:

*   Option
*   Result
*   ...

## Effects in Expression

`expression` offers a clean way to manage effects, allowing you to work with wrapped values without explicit error checking.

```python
from expression import effect, Option, Some, Nothing


def divide(a: float, divisor: float) -> Option[float]:
    try:
        return Some(a / divisor)
    except ZeroDivisionError:
        return Nothing


@effect.option[float]()
def comp(x: float):
    result: float = yield from divide(42, x)
    result += 32
    return result


comp(42)
```

In this example:

*   `divide` returns an `Option[float]`, representing either a successful division (`Some`) or a division by zero (`Nothing`).
*   The `@effect.option[float]()` decorator transforms `comp` into an effectful computation.
*   `yield from divide(42, x)` unwraps the `Option` returned by `divide`. If `divide` returns `Nothing`, the entire `comp` function short-circuits and returns `Nothing`. If `divide` returns `Some(value)`, `result` is assigned the unwrapped `value`.
*   The rest of the computation proceeds only if the `Option` was a `Some`.

This approach eliminates the need for manual `if/else` checks for `None` or exceptions, leading to more concise and readable code.
