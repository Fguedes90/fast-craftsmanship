# Result

## Contents
1. [Overview](#overview)
2. [Type Comparison](#type-comparison)
3. [API Reference](#api-reference)
   - [Creation Methods](#creation-methods)
   - [Transform Methods](#transform-methods)
   - [Access Methods](#access-methods)
4. [Common Patterns](#common-patterns)
5. [Railway Oriented Programming](#railway-oriented-programming)
6. [Integration Patterns](#integration-patterns)
7. [Best Practices](#best-practices)
8. [Testing Patterns](#testing-patterns)
9. [Recipes](#recipes)

## Overview
Result represents computations that can fail, providing type-safe error handling without exceptions. It enables Railway Oriented Programming by explicitly handling both success and failure paths.

## Type Comparison
| Type | Purpose | Alternative To | Best For |
|------|---------|---------------|-----------|
| Result | Error handling | Exceptions | Expected failures |
| Try | Exception handling | try/except | IO operations |
| Option | Optional values | None/null | Missing data |

## API Reference

### Creation Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `ok(x)` | Success value | `Result.ok(42)` | [Common Patterns](#validation-chain) |
| `error(e)` | Error value | `Result.error("Invalid")` | [Railway Patterns](#basic-chain) |
| `catch(f)` | From function | `Result.catch(risky_op)` | [Integration Patterns](#result-with-try) |
| `sequence(xs)` | Combine Results | `Result.sequence(results)` | [Error Aggregation](#error-aggregation) |

### Transform Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `map(f)` | Transform success | `res.map(str)` | [Common Patterns](#safe-operations) |
| `map_error(f)` | Transform error | `res.map_error(str)` | [Error Handling](#error-accumulation) |
| `bind(f)` | Chain Results | `res.bind(validate)` | [Railway Patterns](#basic-chain) |
| `ensure(f)` | Side effect | `res.ensure(cleanup)` | [Resource Management](#resource-management) |

### Access Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `match(ok,err)` | Pattern match | `res.match(str, handle_err)` | [Best Practices](#do-) |
| `value/error` | Unsafe access | `res.value  # Can raise` | [Best Practices](#dont-) |
| `is_ok/is_error` | Check state | `res.is_ok()` | [Testing Patterns](#unit-tests) |
| `to_option()` | Convert to Option | `res.to_option()` | [Integration Patterns](#result-with-option) |

## Common Patterns

### Validation Chain
```python
def validate_user(data: dict) -> Result[User, str]:
    """Validate user data with chained operations."""
    return (Result.ok(data)
        .bind(validate_required_fields)
        .bind(validate_field_types)
        .bind(lambda d: validate_age(d.get("age")))
        .bind(lambda d: validate_email(d.get("email")))
        .map(create_user))

def validate_age(age: int) -> Result[int, str]:
    """Validate age with early returns."""
    return (Result.ok(age)
        .bind(lambda x: 
            Result.ok(x) if x >= 0 
            else Result.error("Age must be positive"))
        .bind(lambda x: 
            Result.ok(x) if x <= 150
            else Result.error("Age too high")))
```

### Error Accumulation
```python
def validate_all(data: dict) -> Result[dict, list[str]]:
    """Accumulate all validation errors."""
    errors = []
    
    def validate_field(key: str, 
                      validator: Callable[[Any], Result[Any, str]]
    ) -> Option[Any]:
        return (Option.of_obj(data.get(key))
            .bind(validator)
            .match(
                lambda ok: Option.some(ok),
                lambda err: errors.append(err) or Option.none()
            ))
    
    name = validate_field("name", validate_name)
    email = validate_field("email", validate_email)
    age = validate_field("age", validate_age)
    
    return (Result.ok({
            "name": name.value,
            "email": email.value,
            "age": age.value
        }) if not errors
        else Result.error(errors))
```

### Resource Management
```python
@contextmanager
def managed_resource(resource: str) -> Iterator[Result[Resource, str]]:
    """Safe resource management with Result."""
    res = None
    try:
        res = setup_resource(resource)
        yield Result.ok(res)
    except Exception as e:
        yield Result.error(f"Resource error: {e}")
    finally:
        if res:
            cleanup_resource(res)

def use_resource(path: str) -> Result[Data, str]:
    """Use resource safely."""
    with managed_resource(path) as result:
        return result.bind(process_resource)
```

## Railway Oriented Programming

### Basic Chain
```python
def process_data(data: dict) -> Result[Output, str]:
    """Railway oriented data processing."""
    return (Result.ok(data)
        .bind(validate_input)    # Switch to error track if invalid
        .bind(enrich_data)       # Continue on success track
        .map(transform_output)   # Transform success value
        .map_error(format_error)) # Transform error value

def validate_input(data: dict) -> Result[dict, str]:
    """Validation switch."""
    return (Result.ok(data)
        if all(required in data for required in REQUIRED_FIELDS)
        else Result.error("Missing required fields"))
```

### Error Aggregation
```python
def process_batch(items: Block[dict]) -> Result[Block[Output], list[str]]:
    """Process batch collecting all errors."""
    results = items.map(process_data)
    
    successes = results.choose(lambda r: r.to_option())
    errors = results.choose(lambda r: 
        Option.some(r.error) if r.is_error() 
        else Option.none())
    
    return (Result.ok(successes) if not errors
            else Result.error(list(errors)))
```

### Parallel Tracks
```python
def validate_parallel(data: dict) -> Result[dict, list[str]]:
    """Run validations in parallel tracks."""
    name_result = validate_name(data.get("name"))
    email_result = validate_email(data.get("email"))
    age_result = validate_age(data.get("age"))
    
    def combine_errors(results: Block[Result[Any, str]]) -> list[str]:
        return list(results
            .choose(lambda r: 
                Option.some(r.error) if r.is_error() 
                else Option.none()))
    
    results = Block.of(name_result, email_result, age_result)
    errors = combine_errors(results)
    
    return (Result.ok(data) if not errors
            else Result.error(errors))
```

## Integration Patterns

### Result with Try
```python
def safe_operation() -> Result[Output, str]:
    """Convert Try to Result."""
    return (Try.catch(risky_operation)
        .to_result()
        .map_error(str))

def load_file(path: str) -> Result[str, str]:
    """Handle IO operations."""
    return (Try.catch(lambda: open(path).read())
        .to_result()
        .map_error(lambda e: f"File error: {e}"))
```

### Result with Option
```python
def find_user(id: str) -> Result[User, str]:
    """Convert Option to Result."""
    return (find_user_optional(id)
        .to_result(f"User {id} not found")
        .bind(validate_user))

def extract_value(data: dict, key: str) -> Result[Any, str]:
    """Handle optional dictionary values."""
    return (Option.of_obj(data.get(key))
        .to_result(f"Missing required field: {key}"))
```

### With Collections
```python
def process_items(items: Block[T]) -> Result[Block[R], list[str]]:
    """Process collection with error aggregation."""
    return Result.traverse(items, safe_process)

def filter_successes(items: Block[Result[T, E]]) -> Block[T]:
    """Keep only successful results."""
    return items.choose(lambda r: r.to_option())
```

## Best Practices

### DO ✓
- Use pattern matching consistently
- Chain operations fluently
- Handle both success/error cases
- Return early on validation
- Use specific error types
- Keep functions pure
- Document error conditions

### DON'T ✗
- Access value/error directly
- Mix with exceptions
- Ignore error cases
- Use for optional values
- Return None for errors
- Nest Results deeply
- Hide error contexts

## Error Handling Patterns

### Railway Oriented Error Handling
```python
def process_with_context(data: dict) -> Result[Output, Error]:
    """Railway oriented error handling with context."""
    def add_context(error: str, context: str) -> Error:
        return Error(message=error, context=context)
    
    return (Result.ok(data)
        .bind(lambda d: 
            validate_input(d)
            .map_error(lambda e: add_context(e, "validation")))
        .bind(lambda d:
            transform_data(d)
            .map_error(lambda e: add_context(e, "transformation")))
        .bind(lambda d:
            save_data(d)
            .map_error(lambda e: add_context(e, "persistence"))))
```

### Error Type Hierarchy
```python
@dataclass(frozen=True)
class Error:
    message: str
    context: str = ""
    source: Optional[Exception] = None

def with_error_context(
    operation: Callable[[], Result[T, str]],
    context: str
) -> Result[T, Error]:
    """Add context to operation errors."""
    return operation().map_error(lambda e: Error(e, context))

# Usage example
def save_user(user: User) -> Result[User, Error]:
    return with_error_context(
        lambda: db_save(user),
        "database.user.save"
    )
```

### Composable Validation
```python
def validate[T](
    validators: Block[Callable[[T], Result[T, str]]]
) -> Callable[[T], Result[T, list[str]]]:
    """Compose multiple validators."""
    def run_validation(value: T) -> Result[T, list[str]]:
        results = validators.map(lambda v: v(value))
        errors = results.choose(lambda r: 
            Option.some(r.error) if r.is_error() 
            else Option.none())
        
        return (Result.ok(value) if not errors
                else Result.error(list(errors)))
    
    return run_validation

# Usage example
validate_user = validate(Block.of(
    validate_name,
    validate_email,
    validate_age
))
```

### Recoverable Errors
```python
def with_recovery[T](
    operation: Callable[[], Result[T, str]],
    recovery: Callable[[str], Result[T, str]]
) -> Result[T, str]:
    """Try operation with recovery strategy."""
    return operation().match(
        lambda ok: Result.ok(ok),
        lambda err: recovery(err)
    )

# Usage example
def load_config(path: str) -> Result[Config, str]:
    return with_recovery(
        lambda: load_main_config(path),
        lambda _: load_fallback_config()
    )
```

## Functional Integration Patterns

### With Monadic Types
```python
def chain_operations[T, R](
    data: T,
    operations: Block[Callable[[T], Result[T, str]]]
) -> Result[T, list[str]]:
    """Chain operations collecting all errors."""
    return operations.fold(
        lambda acc, op: acc.bind(op),
        Result.ok(data)
    )

def traverse_options[T, R](
    items: Block[Option[T]],
    f: Callable[[T], Result[R, str]]
) -> Result[Block[R], list[str]]:
    """Process optional values safely."""
    return (Result.sequence(
        items.choose(lambda o: 
            o.map(f).default_value(Result.ok(None)))
    ).map(lambda xs: xs.filter(lambda x: x is not None)))
```

### With Applicative Validation
```python
def validate_fields[T](
    data: dict,
    validators: Map[str, Callable[[Any], Result[T, str]]]
) -> Result[Map[str, T], list[str]]:
    """Validate multiple fields collecting all errors."""
    results = validators.map(lambda k, v:
        Option.of_obj(data.get(k))
        .map(v)
        .default_value(Result.error(f"Missing field: {k}")))
    
    errors = results.values().choose(lambda r:
        Option.some(r.error) if r.is_error()
        else Option.none())
    
    return (Result.ok(results.filter(lambda _, r: r.is_ok())
                            .map(lambda _, r: r.value))
            if not errors
            else Result.error(list(errors)))
```

### With State Management
```python
@dataclass(frozen=True)
class State[T]:
    value: T
    history: Block[T] = Block.empty()

def state_transition[T](
    current: State[T],
    operation: Callable[[T], Result[T, str]]
) -> Result[State[T], str]:
    """Type-safe state transition."""
    return (Result.ok(current.value)
        .bind(operation)
        .map(lambda new_value: State(
            value=new_value,
            history=current.history.cons(current.value)
        )))

# Usage example
def update_user(state: State[User], 
                update: dict) -> Result[State[User], str]:
    return state_transition(state, lambda user:
        validate_update(update)
        .map(lambda u: apply_update(user, u)))
```

## Testing Patterns

### Unit Tests
```python
def test_result_operations():
    # Test success case
    assert Result.ok(42).map(str).value == "42"
    
    # Test error case
    assert Result.error("error").map(str).is_error()
    
    # Test pattern matching
    result = Result.ok(42).match(
        lambda x: f"Got {x}",
        lambda e: f"Error: {e}"
    )
    assert result == "Got 42"
```

### Property Tests
```python
@given(st.integers())
def test_result_laws(x: int):
    # Identity law
    res = Result.ok(x)
    assert res.map(lambda x: x) == res
    
    # Error propagation
    err = Result.error("error")
    assert err.map(lambda x: x * 2).is_error()
```

### Integration Tests
```python
def test_validation_chain():
    def validate(data: dict) -> Result[User, str]:
        return (Result.ok(data)
            .bind(validate_name)
            .bind(validate_age)
            .map(User.create))
    
    # Test valid data
    valid = {'name': 'Alice', 'age': 25}
    assert validate(valid).is_ok()
    
    # Test invalid data
    invalid = {'name': '', 'age': -1}
    assert validate(invalid).is_error()
```

### Property-Based Testing
```python
@given(st.dictionaries(st.text(), st.integers()))
def test_result_properties(data: dict):
    """Test Result type laws."""
    def success_path(x: Result[int, str]) -> Result[int, str]:
        return x.map(lambda n: n * 2)
    
    def failure_path(x: Result[int, str]) -> Result[int, str]:
        return x.map_error(lambda e: f"Error: {e}")
    
    # Identity
    r = Result.ok(42)
    assert r.map(lambda x: x) == r
    
    # Error propagation
    e = Result.error("error")
    assert e.bind(success_path).is_error()
    
    # Transformation composition
    assert (r.map(str).map(len) == 
            r.map(lambda x: len(str(x))))
```

### Integration Testing
```python
def test_validation_chain():
    """Test complete validation chain."""
    def validate(data: dict) -> Result[User, list[str]]:
        return (Result.ok(data)
            .bind(validate_fields)
            .bind(create_user)
            .ensure(save_user))
    
    valid = {"name": "Alice", "email": "alice@test.com"}
    invalid = {"name": "", "email": "invalid"}
    
    assert validate(valid).is_ok()
    assert validate(invalid).is_error()
    assert len(validate(invalid).error) == 2
```

### Mock Integration
```python
def test_external_integration(mocker):
    """Test integration with external systems."""
    mock_api = mocker.patch("api.call")
    mock_api.return_value = {"status": "success"}
    
    result = api_operation()
    assert result.is_ok()
    assert mock_api.called_once()
    
    mock_api.side_effect = Exception("API Error")
    result = api_operation()
    assert result.is_error()
    assert "API Error" in result.error
```

## Recipes

### API Integration
```python
def api_request(url: str) -> Result[dict, str]:
    """Type-safe API request handling."""
    return (Try.catch(lambda: requests.get(url))
        .to_result()
        .map_error(lambda e: f"Request failed: {e}")
        .bind(lambda r: 
            Try.catch(lambda: r.json())
            .to_result()
            .map_error(lambda e: f"Invalid JSON: {e}")
        ))
```

### Database Operations
```python
def execute_query(query: str, 
                 params: tuple) -> Result[list[tuple], str]:
    """Safe database query execution."""
    def run_query():
        with connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
            
    return (Try.catch(run_query)
        .to_result()
        .map_error(lambda e: f"Database error: {e}"))
```

### Form Validation
```python
def validate_form(data: dict) -> Result[dict, list[str]]:
    """Validate form with error accumulation."""
    errors = []
    
    def validate_field(key: str, 
                      validator: Callable[[Any], Result[Any, str]]
    ) -> Option[Any]:
        return (Option.of_obj(data.get(key))
            .bind(validator)
            .match(
                lambda ok: Option.some(ok),
                lambda err: errors.append(err) or Option.none()
            ))
    
    validated = {
        "email": validate_field("email", validate_email),
        "name": validate_field("name", validate_name),
        "age": validate_field("age", validate_age)
    }
    
    return (Result.ok({
            k: v.value for k, v in validated.items()
        }) if not errors
        else Result.error(errors))