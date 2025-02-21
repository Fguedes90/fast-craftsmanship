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
(tutorial_railway)=

# Railway Oriented Programming with Expression Library

## Core Concepts

Railway Oriented Programming (ROP) is a functional approach to handling errors and composing functions that can fail. The Expression library implements this pattern through its Result type.

## Basic Error Handling

```python
from expression import Result, Success, Failure
from typing import Any

# DO ✅
def parse_int(value: Any) -> Result[int]:
    try:
        return Success(int(value))
    except (ValueError, TypeError):
        return Failure(f"Cannot convert {value} to integer")

def validate_positive(n: int) -> Result[int]:
    return Success(n) if n > 0 else Failure("Number must be positive")

# Chain validations
def process_number(value: Any) -> Result[int]:
    return (
        parse_int(value)
        .bind(validate_positive)
    )

# DON'T ❌
def process_number_unsafe(value: Any) -> int:
    try:
        num = int(value)
        if num <= 0:
            raise ValueError("Number must be positive")
        return num
    except (ValueError, TypeError) as e:
        raise ValueError(str(e))

# WHY: Result type makes error paths explicit and composable
```

## Function Composition with Results

```python
from dataclasses import dataclass
from typing import Optional

# DO ✅
@dataclass(frozen=True)
class User:
    id: str
    name: str
    age: int

def validate_name(name: Optional[str]) -> Result[str]:
    return (
        Success(name)
        if name and name.strip()
        else Failure("Name cannot be empty")
    )

def validate_age(age: Any) -> Result[int]:
    return (
        parse_int(age)
        .bind(lambda n:
            Success(n) if 0 <= n <= 120
            else Failure("Age must be between 0 and 120")
        )
    )

def create_user(data: dict) -> Result[User]:
    from expression.core import pipe
    
    extract_name = lambda t: validate_name(t[0])
    build_name_tuple = lambda name: (name, data.get("age"))
    extract_age = lambda t: validate_age(t[1])
    build_user = lambda age: User(
        id=data.get("id", ""),
        name=t[0],
        age=age
    )

    return pipe(
        Success((data.get("name"), data.get("age"))),
        lambda t: extract_name(t).map(build_name_tuple),
        lambda t: extract_age(t).map(build_user)
    )

# DON'T ❌
def create_user_with_exceptions(data: dict) -> User:
    if not data.get("name"):
        raise ValueError("Name cannot be empty")
    try:
        age = int(data.get("age", ""))
        if not (0 <= age <= 120):
            raise ValueError("Invalid age")
    except ValueError:
        raise ValueError("Invalid age format")
    return User(id=data.get("id", ""), name=data["name"], age=age)

# WHY: Railway style makes validation chains clear and maintainable
```

## Error Aggregation

```python
from expression.collections import Block
from typing import List

# DO ✅
def validate_users(users_data: List[dict]) -> Result[Block[User]]:
    results = Block.of_seq([
        create_user(data) for data in users_data
    ])
    
    is_success = lambda r: r.is_success()
    is_failure = lambda r: r.is_failure()
    get_error = lambda r: r.error
    get_value = lambda r: r.value
    
    successes = results.filter(is_success)
    failures = results.filter(is_failure)
    
    return (
        Success(successes.map(get_value))
        if not failures
        else Failure(f"Validation errors: {failures.map(get_error)}")
    )

# DON'T ❌
def validate_users_unsafe(users_data: List[dict]) -> List[User]:
    valid_users = []
    errors = []
    for data in users_data:
        try:
            user = create_user_with_exceptions(data)
            valid_users.append(user)
        except ValueError as e:
            errors.append(str(e))
    if errors:
        raise ValueError(f"Validation errors: {errors}")
    return valid_users

# WHY: Result allows clean handling of multiple potential failures
```

## Best Practices

### DO ✅
- Use Result for operations that can fail
- Chain validations with bind
- Map successful results with map
- Aggregate errors meaningfully
- Keep validation functions pure

### DON'T ❌
- Use exceptions for control flow
- Mix Result with try/except
- Return null or error strings
- Mutate data during validation
- Nest error handling deeply

## Practical Example

```python
from typing import Dict

# DO ✅
def validate_required(value: Any, field: str) -> Result[Any]:
    return (
        Success(value)
        if value is not None
        else Failure(f"{field} is required")
    )

def validate_email(email: str) -> Result[str]:
    return (
        Success(email)
        if "@" in email and "." in email
        else Failure("Invalid email format")
    )

def validate_form(data: Dict[str, Any]) -> Result[Dict[str, Any]]:
    build_form = lambda email, name: {
        "email": email,
        "name": name
    }

    validate_name_field = lambda email: (
        validate_required(data.get("name"), "Name")
        .bind(validate_name)
        .map(lambda name: build_form(email, name))
    )

    return (
        validate_required(data.get("email"), "Email")
        .bind(validate_email)
        .bind(validate_name_field)
    )

# Usage
form_data = {
    "email": "test@example.com",
    "name": "John Doe"
}

result = validate_form(form_data)
assert result.is_success()

# Test invalid data
invalid_data = {
    "email": "invalid-email",
    "name": ""
}

result = validate_form(invalid_data)
assert result.is_failure()
assert "Invalid email format" in result.error
```

## Testing Example

```python
def test_user_validation():
    # Valid data
    good_data = {
        "id": "1",
        "name": "Alice",
        "age": "25"
    }
    result = create_user(good_data)
    assert result.is_success()
    assert result.value.name == "Alice"
    
    # Invalid data
    bad_data = {
        "id": "2",
        "name": "",
        "age": "invalid"
    }
    result = create_user(bad_data)
    assert result.is_failure()
    assert "Name cannot be empty" in result.error

def test_bulk_validation():
    users_data = [
        {"name": "Alice", "age": "25"},
        {"name": "", "age": "30"},     # Invalid name
        {"name": "Bob", "age": "abc"}  # Invalid age
    ]
    
    result = validate_users(users_data)
    assert result.is_failure()
    assert "Validation errors" in result.error
