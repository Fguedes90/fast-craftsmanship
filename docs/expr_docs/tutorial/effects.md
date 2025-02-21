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
(tutorial_effects)=

# Effects and Side-effects

What are effects? What are side-effects?


## Referential Transparency

Is the result of an expression the same every time you evaluate it? Can you substitute an expression with the value? In functional programming the answer is always yes!

What about Python?

```python
z = [42]

def expr(a):
    #return a + 1

    a += int(input())
    return a
    #print(a)
    #z[0] += a
    #return z[0]
```

Are these programs the same?

```python
a = expr(42)
a, a
```

```python
expr(42), expr(42)
```

We need to be very careful with non-pure functions. Always look out for code smell:

1. Functions or methods that takes no arguments, i.e `Callable[[None], Result]`
2. Functions or methods that returns nothing, i.e `Callable[..., None]`
3. Functions that takes nothing and returns nothing `Callable[[], None]`


## Side Effects

Functions that are not referenctial transparent

Look out for functions that either takes or returns `None`. They are not composable. What do these two functions do?

```python
def get() -> str:
    ...


def put(text: str) -> None:
    ...
```

How can we fix the problem? The solution is that the functions should take and return something to make them pure

```python
from typing import Generic, Tuple, TypeVar

TSource = TypeVar("TSource")

class Io(Generic[TSource]):
    def __init__(self, fn):
        self.__fn = fn  # a world changing function

    def rtn(a) -> "Io[TSource]":
        return Io(lambda world: (a, world + 1))

    def run(self, world: int=0) -> Tuple[TSource, int]:
        return self.__fn(world)

    def bind(self, fn: Callable[[TSource], "Io[TSource]"]) -> "Io[TSource]":
        def run(world):
            a, newWorld = self.run(world)
            return fn(a).run(newWorld)
        return Io(run)

    def __repr__(self):
        return "Io"
```

```python
from typing import Callable

def put(string) -> Io[str]:
    def side_effect(_):
        return Io.rtn(print(string))

    return Io.rtn(None).bind(side_effect)

def get(fn: Callable[[str], Io[str]]) -> Io[str]:
    def side_effect(_):
        return fn(input())
    return Io.rtn(None).bind(side_effect)
```

```python
io = put("Hello, what is your name?").bind(
    lambda _: get(
        lambda name: put("What is your age?").bind(
            lambda _: get(
                lambda age: put("Hello %s, your age is %d." % (name, int(age)))
            )
        )
    ))

(io, io)
```

Are they the same? We really don't know. We are not allowed to look inside the box. But we can run the effect:

```python
io.run(world=0)
```

# Effects in Python with Expression Library

## Core Concepts

Effects represent computations that might fail or have side effects. The Expression library provides a powerful Effect type for handling these scenarios safely.

## Basic Effects Usage

```python
from expression import Effect
from typing import Optional

# DO ✅
def get_user(user_id: str) -> Effect[dict]:
    if not user_id:
        return Effect.fail("Invalid user id")
    return Effect.success({"id": user_id, "name": "John"})

def validate_age(user: dict) -> Effect[dict]:
    age = user.get("age")
    if not age or age < 18:
        return Effect.fail("User must be 18 or older")
    return Effect.success(user)

# Chain effects elegantly
def process_user(user_id: str) -> Effect[dict]:
    return (
        get_user(user_id)
        .bind(validate_age)
    )

# DON'T ❌
def process_user_unsafe(user_id: str) -> Optional[dict]:
    if not user_id:
        return None
    user = {"id": user_id, "name": "John"}
    if user.get("age", 0) < 18:
        return None
    return user

# WHY: Effects provide clear error handling and composability
```

## Error Handling

```python
from typing import Union

# DO ✅
def divide(a: float, b: float) -> Effect[float]:
    if b == 0:
        return Effect.fail("Division by zero")
    return Effect.success(a / b)

# Chain with error handling
def complex_calculation(x: float, y: float) -> Effect[float]:
    double_result = lambda result: result * 2
    handle_error = lambda _: Effect.success(0.0)  # Fallback value
    
    return (
        divide(x, y)
        .map(double_result)
        .catch(handle_error)
    )

# DON'T ❌
def divide_unsafe(a: float, b: float) -> Union[float, str]:
    try:
        if b == 0:
            return "Division by zero"
        return a / b
    except Exception as e:
        return str(e)

# WHY: Effects make error paths explicit and composable
```

## Async Effects

```python
from expression import Effect
import asyncio

# DO ✅
async def fetch_data(url: str) -> Effect[dict]:
    return Effect.success({"data": "example"})

async def process_data(data: dict) -> Effect[str]:
    return Effect.success(f"Processed: {data['data']}")

async def handle_request(url: str) -> Effect[str]:
    return (
        await fetch_data(url)
        .bind(process_data)
    ).to_awaitable()

# DON'T ❌
async def handle_request_unsafe(url: str) -> str:
    try:
        data = await fetch_data_unsafe(url)
        if data is None:
            return "Error fetching data"
        return await process_data_unsafe(data)
    except Exception as e:
        return str(e)

# WHY: Effects make async code more predictable and easier to test
```

## Best Practices

### DO ✅
- Use Effect for operations that might fail
- Chain effects with bind and map
- Handle errors explicitly with catch
- Convert to/from async with to_awaitable()
- Use Effect.success/fail for clear outcomes

### DON'T ❌
- Mix Effect with try/except blocks
- Return None or error strings
- Use raw exceptions for control flow
- Mix Effect with Optional types
- Nest effects unnecessarily

## Testing Effects

```python
def test_user_processing():
    # Success case
    result = process_user("123").run()
    assert result.is_success()
    assert result.value["id"] == "123"

    # Failure case
    result = process_user("").run()
    assert result.is_failure()
    assert "Invalid user id" in str(result.error)

def test_complex_calculation():
    # Success case
    result = complex_calculation(10, 2).run()
    assert result.is_success()
    assert result.value == 10.0

    # Failure with fallback
    result = complex_calculation(10, 0).run()
    assert result.is_success()
    assert result.value == 0.0
```

## Practical Example

```python
from expression import Effect
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class User:
    id: str
    name: str
    age: Optional[int] = None

# DO ✅
def create_user(data: dict) -> Effect[User]:
    validate_user_age = lambda user: (
        Effect.fail("Invalid age")
        if user.age is not None and user.age < 0
        else Effect.success(user)
    )

    return (
        Effect.catch(lambda: User(**data))
        .bind(validate_user_age)
    )

def update_user(user: User, updates: dict) -> Effect[User]:
    merge_user_data = lambda: {**user.__dict__, **updates}
    
    return (
        Effect.success(merge_user_data())
        .bind(lambda data: create_user(data))
    )

# Usage example
user_data = {"id": "123", "name": "John", "age": 25}
update_age = {"age": 26}

result = (
    create_user(user_data)
    .bind(lambda user: update_user(user, update_age))
).run()

