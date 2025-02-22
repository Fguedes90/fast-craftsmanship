# Testing with Expression Library

## Overview
This guide covers testing patterns and best practices for code using Expression's functional types and utilities.

## Core Testing Patterns

### Testing Result Types

#### Basic Result Assertions
```python
def test_result_basics():
    # Success case
    success = Ok(42)
    assert success.is_ok()
    assert success.ok == 42
    assert not success.is_error()
    
    # Error case
    error = Error("failed")
    assert error.is_error()
    assert str(error.error) == "failed"
    assert not error.is_ok()
```

#### Testing Transformations
```python
def test_result_transformations():
    # Map
    result = Ok(21).map(lambda x: x * 2)
    assert result.ok == 42
    
    # Bind
    def safe_divide(x: float, y: float) -> Result[float, str]:
        return Ok(x / y) if y != 0 else Error("Division by zero")
    
    result = Ok(10).bind(lambda x: safe_divide(x, 2))
    assert result.ok == 5.0
    
    result = Ok(10).bind(lambda x: safe_divide(x, 0))
    assert result.is_error()
    assert "Division by zero" in str(result.error)
```

### Testing Option Types

#### Basic Option Assertions
```python
def test_option_basics():
    # Some case
    some = Some(42)
    assert some.is_some()
    assert some.value == 42
    assert not some.is_none()
    
    # None case
    none = Nothing
    assert none.is_none()
    assert not none.is_some()
```

#### Testing Option Chains
```python
def test_option_chains():
    def find_user(id: str) -> Option[dict]:
        return Some({"id": id}) if id else Nothing
    
    def get_age(user: dict) -> Option[int]:
        return Some(user.get("age")) if "age" in user else Nothing
    
    # Test successful chain
    result = (Some({"id": "1", "age": 30})
        .bind(get_age)
        .map(lambda age: age + 1))
    assert result.value == 31
    
    # Test broken chain
    result = (Some({"id": "1"})
        .bind(get_age)
        .map(lambda age: age + 1))
    assert result.is_none()
```

## Testing Complex Scenarios

### Validation Chains
```python
def test_validation_chain():
    def validate_required(data: dict) -> Result[dict, str]:
        return (Ok(data) if "name" in data and data["name"]
                else Error("Name required"))
    
    def validate_age(data: dict) -> Result[dict, str]:
        age = data.get("age", 0)
        return Ok(data) if 0 <= age <= 150 else Error("Invalid age")
    
    # Test full chain
    result = (Ok({"name": "Alice", "age": 30})
        .bind(validate_required)
        .bind(validate_age))
    assert result.is_ok()
    
    # Test validation failures
    result = (Ok({"name": "", "age": 30})
        .bind(validate_required)
        .bind(validate_age))
    assert result.is_error()
    assert "Name required" in str(result.error)
```

### Async Operations
```python
@pytest.mark.asyncio
async def test_async_operations():
    async def fetch_user(id: str) -> Result[dict, str]:
        if id == "404":
            return Error("Not found")
        return Ok({"id": id, "name": "Test"})
    
    async def update_user(user: dict) -> Result[dict, str]:
        return Ok({**user, "updated": True})
    
    # Test success path
    result = await fetch_user("123")
    assert result.is_ok()
    
    # Test chained async operations
    result = (await fetch_user("123")
        .bind(update_user))
    assert result.ok["updated"]
    
    # Test failure path
    result = await fetch_user("404")
    assert result.is_error()
```

### Collection Operations
```python
def test_collection_operations():
    from expression.collections import Block, Map
    
    # Test Block operations
    numbers = Block.of(1, 2, 3)
    result = (numbers
        .map(lambda x: x * 2)
        .filter(lambda x: x > 4))
    assert list(result) == [6]
    
    # Test Map operations
    scores = Map.of_seq([("A", 90), ("B", 85)])
    high_scores = scores.filter(lambda _, score: score >= 90)
    assert len(high_scores) == 1
```

## Testing Best Practices

### Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_result_properties(x: int):
    # Identity law
    result = Ok(x)
    assert result.map(lambda x: x) == result
    
    # Composition law
    f = lambda x: x * 2
    g = lambda x: x + 1
    assert (result.map(f).map(g) == 
            result.map(lambda x: g(f(x))))

@given(st.lists(st.integers()))
def test_block_properties(xs: list[int]):
    # Conversion preserves length
    block = Block.of_seq(xs)
    assert len(block) == len(xs)
    
    # Map preserves structure
    mapped = block.map(str)
    assert len(mapped) == len(block)
```

### Error Testing Patterns
```python
def test_error_patterns():
    # Test specific error types
    result = process_data(invalid_input)
    assert isinstance(result.error, ValueError)
    
    # Test error messages
    assert "Invalid input" in str(result.error)
    
    # Test error recovery
    result = result.recover(lambda _: default_value)
    assert result.is_ok()
    
    # Test error transformation
    result = (Error("error")
        .map_error(lambda e: f"Wrapped: {e}")
        .map_error(str.upper))
    assert result.error == "WRAPPED: ERROR"
```

### Integration Testing
```python
def test_full_workflow():
    # Setup test data
    input_data = {"name": "Test", "age": 30}
    
    # Test complete workflow
    result = (Result.ok(input_data)
        .bind(validate_input)
        .bind(transform_data)
        .bind(save_data))
        
    # Verify final state
    assert result.is_ok()
    assert result.ok["processed"]
```

## Common Testing Pitfalls

1. Direct Value Access
   ```python
   # WRONG: May raise if error
   value = result.ok
   
   # RIGHT: Use pattern matching
   value = result.match(
       lambda ok: ok,
       lambda err: default_value
   )
   ```

2. Async Result Handling
   ```python
   # WRONG: Can't await Result
   value = await result
   
   # RIGHT: Await the async function
   result = await async_function()
   ```

3. Collection Comparisons
   ```python
   # WRONG: Block is not a list
   assert block == [1, 2, 3]
   
   # RIGHT: Convert to list first
   assert list(block) == [1, 2, 3]
   ```

## Performance Testing

### Benchmarking Patterns
```python
def test_performance():
    import timeit
    
    def measure_chain():
        return (Ok(42)
            .map(lambda x: x * 2)
            .map(str)
            .map(len))
    
    time = timeit.timeit(measure_chain, number=10000)
    assert time < 1.0  # Should complete within reasonable time
```

### Memory Usage
```python
def test_memory_usage():
    import sys
    
    # Test memory sharing in Block
    large_data = list(range(10000))
    block = Block.of_seq(large_data)
    
    # Adding one item should not copy everything
    new_block = block.cons(0)
    
    # Verify reasonable memory usage
    assert sys.getsizeof(new_block) < sys.getsizeof(large_data)
