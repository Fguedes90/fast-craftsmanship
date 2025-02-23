# Optional Values

In functional programming, we use the Option (or Maybe) type to handle cases where a value might be missing. The Expression library provides an elegant way to work with optional values through its `option` module.

## Creating Options

Import the necessary components:
```python
from expression import Option, option, Some, Nothing
```

Create optional values:

```python
# Some value
x = Some(42)
print(x)  # Some(42)

# No value
y = Nothing
print(y)  # Nothing
```

## Option-Returning Functions

Create safe functions that return options:
```python
def keep_positive(a: int) -> Option[int]:
    return Some(a) if a > 0 else Nothing

def divide(a: float, divisor: float) -> Option[float]:
    try:
        return Some(a/divisor)
    except ZeroDivisionError:
        return Nothing
```

## Transforming Options

Transform options without explicit null checking using `pipe` and `option.map`:
```python
from expression import pipe

result = pipe(
    Some(42),
    option.map(lambda x: x * 10)
)
print(result)  # Some(420)

# Nothing values propagate through transformations
result = pipe(
    Nothing,
    option.map(lambda x: x * 10)
)
print(result)  # Nothing
```

## Option Effects

Use the `@effect.option` decorator for railway-oriented programming:

```python
from expression import effect

@effect.option[int]()
def calculate():
    x = yield 42
    y = yield from Some(43)
    return x + y

result = calculate()
print(result)  # Some(85)

@effect.option[int]()
def failing_calculation():
    x = yield from Nothing
    # Following code won't execute
    y = yield from Some(43)
    return x + y

result = failing_calculation()
print(result)  # Nothing
```

For more information, check the [API reference](https://expression.readthedocs.io/en/latest/reference/option.html).
