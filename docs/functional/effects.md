# Effect Functions

Effect functions provide a powerful way to handle sequences of operations that may fail, while maintaining composability and error handling.

## Overview

In Railway Oriented Programming, operations that may fail return a `Result` type. When you need to chain multiple operations where each depends on the result of the previous one, using `bind` or `pipeline` can become verbose and hard to read.

Effect functions solve this problem by using generator-based functions with the `@effect.result` decorator.

## Basic Structure

An effect function has this general structure:

```python
from expression import effect, Result, Ok, Error

@effect.result[ReturnType, ErrorType]()
def process_data(input_data):
    # Yield from operation 1, which returns a Result
    intermediate_result = yield from operation1(input_data)
    
    # Yield from operation 2, which also returns a Result
    final_result = yield from operation2(intermediate_result)
    
    # Return the final result (will be wrapped in Ok)
    return final_result
```

## How It Works

1. The function is decorated with `@effect.result[ReturnType, ErrorType]()`
2. Inside the function, operations are performed using `yield from` with functions that return `Result` objects
3. If any operation returns an `Error`, execution stops and the error is propagated
4. If all operations succeed, the final `return` value is wrapped in an `Ok`

## Example: User Processing

```python
from expression import effect, Result, Ok, Error
from pydantic import BaseModel

class User(BaseModel):
    id: str
    name: str

class Profile(BaseModel):
    user_id: str
    preferences: dict

class Settings(BaseModel):
    theme: str
    notifications: bool

def get_user(user_id: str) -> Result[User, str]:
    # Simulated database lookup
    if user_id == "123":
        return Ok(User(id="123", name="Alice"))
    return Error(f"User not found: {user_id}")

def get_profile(user: User) -> Result[Profile, str]:
    # Simulated profile lookup
    if user.id == "123":
        return Ok(Profile(user_id=user.id, preferences={"language": "en"}))
    return Error(f"Profile not found for user: {user.id}")

def get_settings(profile: Profile) -> Result[Settings, str]:
    # Get settings based on profile
    lang = profile.preferences.get("language", "en")
    if lang == "en":
        return Ok(Settings(theme="light", notifications=True))
    return Error(f"Settings not available for language: {lang}")

@effect.result[Settings, str]()
def get_user_settings(user_id: str):
    # The effect function chains the operations
    user = yield from get_user(user_id)
    profile = yield from get_profile(user)
    settings = yield from get_settings(profile)
    return settings

# Usage:
result = get_user_settings("123")  # Ok(Settings(theme='light', notifications=True))
result = get_user_settings("456")  # Error("User not found: 456")
```

## Early Returns

You can return early from an effect function by using `yield Error(...)` followed by a `return` statement:

```python
@effect.result[str, str]()
def process_user(user_id: str):
    # Check if user ID is valid
    if not user_id:
        yield Error("User ID cannot be empty")
        return  # Early return after yielding an Error
    
    user = yield from get_user(user_id)
    # Continue with the rest of the function...
    return f"Processed user: {user.name}"
```

## Working with Optional Values

You can easily handle `Option` types within effect functions:

```python
from expression import effect, Result, Ok, Error, Option, Some, Nothing

def find_user(user_id: str) -> Option[User]:
    # Returns Some(user) or Nothing
    
@effect.result[User, str]()
def process_optional_user(user_id: str):
    option_user = find_user(user_id)
    
    match option_user:
        case Some(user):
            return user
        case Nothing:
            yield Error(f"User not found: {user_id}")
            return  # Early return after yielding an Error
```

## Testing Effect Functions

Testing effect functions requires special attention:

```python
# Option 1: Use @effect.result in the test function
def test_get_user_settings():
    @effect.result[None, None]()
    def run_test():
        result = yield from get_user_settings("123")
        assert result.is_ok()
        assert result.ok.theme == "light"
    
    run_test()  # Run the effect function

# Option 2: Collect the final result by iterating the generator
def test_get_user_settings_with_iteration():
    final_result = None
    for step in get_user_settings("123"):
        final_result = step
    
    assert final_result.is_ok()
    assert final_result.ok.theme == "light"
```

## Mocking in Tests

When testing code that uses effect functions, you may need to mock other effect functions:

```python
def test_with_mocks(monkeypatch):
    @effect.result[User, str]()
    def mock_get_user(user_id: str):
        yield Ok(User(id=user_id, name="Mock User"))
    
    monkeypatch.setattr("module.get_user", mock_get_user)
    
    @effect.result[None, None]()
    def run_test():
        result = yield from get_user_settings("mock_id")
        assert result.is_ok()
    
    run_test()
```

## Alternatives to Effect Functions

When should you use effect functions versus other approaches?

| Approach | When to Use |
| -------- | ----------- |
| Effect Functions | Sequential operations with dependency between steps |
| Pipeline | Independent operations in a chain |
| Pattern Matching | Simple, non-sequential error handling |
| Map/Bind | When you need manual control of the flow |

Effect functions are particularly useful when:

1. Each step depends on the result of the previous step
2. You want to maintain clean, readable code
3. You need early returns based on conditions
4. You're replacing async/await patterns