# Testing with Expression Library

This guide explains how to write tests for code that uses the Expression library's Result and Option types.

## Testing Result Types

When testing functions that return `Result` types, you should use these methods:

### Checking Result Status

```python
# Check if result is successful
assert result.is_ok()

# Check if result is an error
assert result.is_error()
```

### Accessing Result Values

```python
# Access success value using .ok property
assert result.ok == expected_value

# Access error value using .error property
assert result.error == expected_error
assert isinstance(result.error, ValueError)  # Check error type
assert str(result.error) == "expected error message"
```

### Example: Testing Success Case

```python
def test_successful_operation():
    result = some_function()
    assert result.is_ok()
    assert result.ok == "expected value"
```

### Example: Testing Error Case

```python
def test_failed_operation():
    result = some_function()
    assert result.is_error()
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "expected error message"
```

## Testing Option Types

When testing functions that return `Option` types:

### Creating Options

```python
from expression import Some, Nothing

# Create Some value
some_value = Some(42)

# Create Nothing value
nothing = Nothing
```

### Testing Option Results

```python
def test_option_with_value():
    result = get_optional_value()
    assert result == Some(expected_value)

def test_option_with_nothing():
    result = get_optional_value()
    assert result == Nothing
```

## Testing Railway-Oriented Programming (ROP)

When testing functions that use ROP patterns:

### Testing Function Composition

```python
def test_compose_validations():
    first_validation = validate(lambda x: x > 0, "Must be positive")
    second_validation = validate(lambda x: x < 10, "Must be less than 10")
    
    composed = compose_validations(first_validation, second_validation)
    
    # Test success case
    result = composed(5)
    assert result.is_ok()
    assert result.ok == 5
    
    # Test failure case
    result = composed(-5)
    assert result.is_error()
    assert "Must be positive" in str(result.error)
```

### Testing Result Sequences

```python
def test_sequence_results():
    results = [Ok(1), Ok(2), Ok(3)]
    combined = sequence_results(results)
    assert combined.is_ok()
    assert combined.ok == [1, 2, 3]

def test_sequence_with_failure():
    error = ValueError("test error")
    results = [Ok(1), Error(error), Ok(3)]
    combined = sequence_results(results)
    assert combined.is_error()
    assert combined.error == error
```

## Testing Async Functions

When testing async functions that return Results:

```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await async_operation()
    assert result.is_ok()
    assert result.ok == "expected value"

@pytest.mark.asyncio
async def test_async_operation_failure():
    result = await async_operation()
    assert result.is_error()
    assert isinstance(result.error, ValueError)
```

## Best Practices

1. Always test both success and failure cases
2. Check both the status (.is_ok()/.is_error()) and the value (.ok/.error)
3. For error cases, verify both the error type and message
4. Use pytest.mark.asyncio for async function tests
5. Test edge cases and boundary conditions
6. For composed functions, test each component separately first

## Common Pitfalls

1. Using .ok() or .error() as methods - they are properties
2. Not handling async functions properly with pytest.mark.asyncio
3. Not checking both status and value in tests
4. Forgetting to test error messages and types
5. Not testing the full chain in composed functions

## Practical Examples

### 1. Testing Validation Functions

```python
from expression import Result, Ok, Error

def validate_age(age: int) -> Result[int, Exception]:
    if age < 0:
        return Error(ValueError("Age cannot be negative"))
    if age > 150:
        return Error(ValueError("Age seems unrealistic"))
    return Ok(age)

def test_validate_age():
    # Test valid age
    result = validate_age(25)
    assert result.is_ok()
    assert result.ok == 25

    # Test negative age
    result = validate_age(-1)
    assert result.is_error()
    assert isinstance(result.error, ValueError)
    assert str(result.error) == "Age cannot be negative"

    # Test unrealistic age
    result = validate_age(200)
    assert result.is_error()
    assert str(result.error) == "Age seems unrealistic"
```

### 2. Testing Data Transformation Chain

```python
from expression import Result, Ok, Error
from dataclasses import dataclass
from typing import Callable

@dataclass
class User:
    name: str
    age: int

def validate_name(name: str) -> Result[str, Exception]:
    if not name.strip():
        return Error(ValueError("Name cannot be empty"))
    return Ok(name)

def create_user(name: str, age: int) -> Result[User, Exception]:
    return (
        validate_name(name)
        .bind(lambda valid_name: validate_age(age))
        .map(lambda valid_age: User(name=name, age=valid_age))
    )

def test_user_creation():
    # Test successful creation
    result = create_user("Alice", 30)
    assert result.is_ok()
    assert result.ok == User(name="Alice", age=30)

    # Test invalid name
    result = create_user("", 30)
    assert result.is_error()
    assert str(result.error) == "Name cannot be empty"

    # Test invalid age
    result = create_user("Bob", -1)
    assert result.is_error()
    assert str(result.error) == "Age cannot be negative"
```

### 3. Testing Async Operations

```python
from expression import Result, Ok, Error
import pytest
from typing import Optional

async def fetch_user_data(user_id: str) -> Result[dict, Exception]:
    if user_id == "404":
        return Error(ValueError("User not found"))
    return Ok({"id": user_id, "name": "Test User"})

async def update_user(user_id: str, data: dict) -> Result[dict, Exception]:
    fetch_result = await fetch_user_data(user_id)
    return (
        fetch_result
        .map(lambda user: {**user, **data})
    )

@pytest.mark.asyncio
async def test_update_user():
    # Test successful update
    result = await update_user("123", {"name": "Updated Name"})
    assert result.is_ok()
    assert result.ok == {"id": "123", "name": "Updated Name"}

    # Test non-existent user
    result = await update_user("404", {"name": "New Name"})
    assert result.is_error()
    assert str(result.error) == "User not found"
```

### 4. Testing Option Types with Results

```python
from expression import Option, Some, Nothing, Result, Ok, Error

def find_user(user_id: str) -> Option[dict]:
    return Some({"id": user_id}) if user_id else Nothing

def process_user(user_id: str) -> Result[dict, Exception]:
    return (
        Ok(find_user(user_id))
        .bind(lambda user_opt: 
            Ok(user_opt.value) if user_opt != Nothing 
            else Error(ValueError("User not found"))
        )
    )

def test_process_user():
    # Test existing user
    result = process_user("123")
    assert result.is_ok()
    assert result.ok == {"id": "123"}

    # Test missing user
    result = process_user("")
    assert result.is_error()
    assert str(result.error) == "User not found"
```

## Tips for Test Organization

1. Group related tests in test classes
2. Use descriptive test names that indicate the scenario being tested
3. Follow the Arrange-Act-Assert pattern
4. Create helper functions for common test setups
5. Use pytest fixtures for complex test scenarios

Example of well-organized tests:

```python
@pytest.mark.asyncio
class TestUserOperations:
    @pytest.fixture
    async def test_user(self):
        return {"id": "test-id", "name": "Test User"}

    async def test_successful_user_update(self, test_user):
        # Arrange
        update_data = {"name": "Updated Name"}
        
        # Act
        result = await update_user(test_user["id"], update_data)
        
        # Assert
        assert result.is_ok()
        assert result.ok["name"] == "Updated Name"
        assert result.ok["id"] == test_user["id"]

    async def test_failed_user_update(self):
        # Arrange
        update_data = {"name": "Updated Name"}
        
        # Act
        result = await update_user("404", update_data)
        
        # Assert
        assert result.is_error()
        assert isinstance(result.error, ValueError)
        assert str(result.error) == "User not found"
```

## Debugging and Troubleshooting

### Common Testing Issues

1. **Pattern Matching Issues**
```python
# INCORRECT - Will raise TypeError
match result:
    case Ok(value):  # TypeError: called match pattern must be a class
        ...

# CORRECT - Use if/else or match on result.is_ok()
if result.is_ok():
    value = result.ok
    ...
```

2. **Async Result Handling**
```python
# INCORRECT - Will raise TypeError
result = await async_fn()  # Returns Result
next_result = await result  # TypeError: 'Result' object cannot be awaited

# CORRECT - Only await the async function
result = await async_fn()  # Returns Result
next_result = result.map(lambda x: x + 1)  # Continue with Result operations
```

3. **Result Value Access**
```python
# INCORRECT - .ok() and .error() as methods
value = result.ok()  # AttributeError: 'Result' object has no attribute 'ok'

# CORRECT - .ok and .error as properties
value = result.ok  # Access success value
error = result.error  # Access error value
```

### Debugging Tips

1. **Print Result State**
```python
def debug_result(result: Result):
    print(f"Is Ok: {result.is_ok()}")
    print(f"Is Error: {result.is_error()}")
    if result.is_ok():
        print(f"Value: {result.ok}")
    else:
        print(f"Error: {result.error}")
```

2. **Using pytest.fail for Debugging**
```python
def test_complex_operation():
    result = complex_operation()
    if result.is_error():
        pytest.fail(f"Operation failed: {result.error}")
    assert result.ok == expected_value
```

3. **Verbose Test Output**
```bash
pytest -vv  # Show full test output including variable values
pytest -vv --tb=short  # Show shorter tracebacks
pytest -vv --pdb  # Drop into debugger on test failure
```

### Testing Result Transformations

1. **Map Operations**
```python
def test_result_map():
    result = Ok(5)
    mapped = result.map(lambda x: x * 2)
    assert mapped.is_ok()
    assert mapped.ok == 10
```

2. **Bind Operations**
```python
def test_result_bind():
    def divide(x: int) -> Result[float, Exception]:
        if x == 0:
            return Error(ValueError("Division by zero"))
        return Ok(1.0 / x)

    result = Ok(2).bind(divide)
    assert result.is_ok()
    assert result.ok == 0.5

    result = Ok(0).bind(divide)
    assert result.is_error()
    assert isinstance(result.error, ValueError)
```

3. **Chain of Operations**
```python
def test_operation_chain():
    def validate(x: int) -> Result[int, Exception]:
        return Ok(x) if x > 0 else Error(ValueError("Must be positive"))
    
    def process(x: int) -> Result[str, Exception]:
        return Ok(str(x))

    result = (
        Ok(42)
        .bind(validate)
        .map(lambda x: x * 2)
        .bind(process)
    )

    assert result.is_ok()
    assert result.ok == "84"
```

### Performance Testing Considerations

1. **Result Creation Overhead**
```python
def test_result_creation_performance():
    import timeit
    
    def create_results():
        return [Ok(i) for i in range(1000)]
    
    time = timeit.timeit(create_results, number=1000)
    assert time < 1.0  # Should complete within reasonable time
```

2. **Chain Operation Performance**
```python
def test_chain_performance():
    import timeit
    
    def complex_chain():
        return (
            Ok(42)
            .map(lambda x: x + 1)
            .map(lambda x: x * 2)
            .map(str)
        )
    
    time = timeit.timeit(complex_chain, number=1000)
    assert time < 1.0  # Should complete within reasonable time
```

Remember: The Expression library is designed for correctness first, so while performance is important, the primary focus should be on writing correct and maintainable code.