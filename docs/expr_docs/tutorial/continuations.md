# Callbacks and Continuations in Python

## Core Concepts

Continuations are a way to handle asynchronous operations and control flow in functional programming. They represent "what happens next" in program execution.

## Continuation Passing Style (CPS)

### Basic Example

```python
# DO ✅
from expression.core import pipe

def process_async(value, on_complete):
    double_value = lambda x: x * 2
    increment_value = lambda x: x + 1
    
    result = pipe(
        value,
        double_value,
        increment_value,
        on_complete
    )
    return result

# DON'T ❌
def nested_callbacks(value, on_complete):
    def step1(x):
        def step2(y):
            on_complete(y + 1)
        step2(x * 2)
    step1(value)

# WHY: Pipe creates cleaner, more readable async operations without callback hell
```

## Modern Continuation Handling

### Using Expression Library

```python
from expression import Effect

# DO ✅
def fetch_user_data(user_id: str) -> Effect:
    return Effect.success({"id": user_id, "name": "John"})

def process_user(user_data: dict) -> Effect:
    return Effect.success(f"Processed {user_data['name']}")

# Chain continuations cleanly
def handle_user(user_id: str) -> Effect:
    process_user_data = lambda data: process_user(data)
    
    return (
        fetch_user_data(user_id)
        .map(process_user_data)
    )

# DON'T ❌
def callback_hell(user_id: str, callback):
    def on_fetch(user_data):
        def on_process(result):
            callback(result)
        process_user(user_data, on_process)
    fetch_user_data(user_id, on_fetch)

# WHY: Effect provides type-safe, composable continuations
```

## Async/Await Integration

```python
from expression import Effect
import asyncio

# DO ✅
async def async_operation():
    effect = Effect.success(42)
    result = await effect.to_awaitable()
    return result

# DON'T ❌
def manual_promise_chain():
    promise = Promise()
    promise.then(lambda x: x * 2).then(print)
    return promise

# WHY: Native async/await syntax is more readable and maintainable
```

## Best Practices

### DO ✅
- Use Effect for composable continuations
- Leverage pipe for sequential operations
- Use async/await with Effect.to_awaitable()
- Keep continuation chains flat and readable

### DON'T ❌
- Nest callbacks deeply
- Mix different continuation styles
- Use raw promises when Effect is available
- Create complex continuation hierarchies

## Testing Continuations

```python
from expression import Effect
import pytest

# DO ✅
def test_user_processing():
    effect = handle_user("user123")
    
    # Test synchronously
    result = effect.run()
    assert "Processed John" in result

# DON'T ❌
def test_with_callbacks(done):
    def callback(result):
        try:
            assert "Processed" in result
            done()
        except Exception as e:
            done(e)
    
    handle_user_callback("user123", callback)

# WHY: Effect makes testing asynchronous code straightforward and deterministic
```

## Key Benefits

1. Type Safety
2. Composability
3. Better Error Handling
4. Testability
5. Integration with async/await

## Practice Example

```python
from expression import Effect

def validate(data: dict) -> Effect:
    return Effect.success(data) if data.get("id") else Effect.fail("Invalid data")

def save(data: dict) -> Effect:
    return Effect.success(f"Saved {data['id']}")

# DO ✅
def process_data(data: dict) -> Effect:
    save_data = lambda x: save(x)
    format_success = lambda x: f"Success: {x}"
    format_error = lambda err: f"Error: {err}"
    
    return (
        validate(data)
        .map(save_data)
        .map(format_success)
        .catch(format_error)
    )

# Test
data = {"id": "123", "value": "test"}
result = process_data(data).run()
assert "Success" in result
