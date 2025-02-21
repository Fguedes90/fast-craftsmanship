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
(tutorial_optional_values)=

# Optional Values in Python with Expression Library

## Core Concepts

Optional values handle the absence of data safely. Expression library's Option type provides a functional approach to handling nullable values.

## Basic Usage

```python
from expression import Option, Some, Nothing
from typing import Optional

# DO ✅
def find_user(user_id: str) -> Option[dict]:
    users = {"1": {"name": "Alice"}, "2": {"name": "Bob"}}
    return Some(users[user_id]) if user_id in users else Nothing

def get_user_name(user: dict) -> Option[str]:
    return Some(user["name"]) if "name" in user else Nothing

# Chain operations safely
def process_user(user_id: str) -> str:
    return (
        find_user(user_id)
        .bind(get_user_name)
        .default_value("User not found")
    )

# DON'T ❌
def find_user_unsafe(user_id: str) -> Optional[dict]:
    users = {"1": {"name": "Alice"}, "2": {"name": "Bob"}}
    return users.get(user_id)

def process_user_unsafe(user_id: str) -> str:
    user = find_user_unsafe(user_id)
    if user is None:
        return "User not found"
    name = user.get("name")
    if name is None:
        return "Name not found"
    return name

# WHY: Option provides safe, chainable operations for nullable values
```

## Pattern Matching

```python
# DO ✅
def describe_user(maybe_user: Option[dict]) -> str:
    match maybe_user:
        case Some(user):
            return f"Found user: {user['name']}"
        case Nothing:
            return "No user found"

# DON'T ❌
def describe_user_unsafe(user: Optional[dict]) -> str:
    if user is None:
        return "No user found"
    return f"Found user: {user['name']}"

# WHY: Pattern matching with Option is more explicit and type-safe
```

## Collections with Options

```python
from expression.collections import Block

# DO ✅
def get_ages(users: Block[dict]) -> Block[int]:
    extract_age = lambda u: Option.from_optional(u.get("age"))
    
    return (
        users
        .map(extract_age)
        .filter_map(lambda x: x)  # Removes None values
    )

# Test data
users = Block.of_seq([
    {"name": "Alice", "age": 30},
    {"name": "Bob"},  # No age
    {"name": "Charlie", "age": 25}
])

ages = get_ages(users)  # Block[30, 25]

# DON'T ❌
def get_ages_unsafe(users: list[dict]) -> list[int]:
    result = []
    for user in users:
        age = user.get("age")
        if age is not None:
            result.append(age)
    return result

# WHY: Option with collections provides clean filtering of nullable values
```

## Best Practices

### DO ✅
- Use Option for potentially missing values
- Chain operations with bind and map
- Provide default values with default_value
- Use pattern matching for clear branching
- Convert Optional to Option with from_optional

### DON'T ❌
- Use None for missing values
- Check for None manually
- Mix Option with Optional
- Raise exceptions for missing values
- Create deeply nested if-checks

## Practical Example

```python
from dataclasses import dataclass
from typing import Optional as Opt  # Rename to avoid confusion

@dataclass(frozen=True)
class User:
    id: str
    name: str
    email: Opt[str] = None
    age: Opt[int] = None

# DO ✅
def validate_email(email: str) -> Option[str]:
    return Some(email) if "@" in email else Nothing

def create_user(data: dict) -> Option[User]:
    validate_id = lambda id: bool(id)  # Ensure non-empty ID
    validate_name = lambda name: bool(name)  # Ensure non-empty name
    build_user = lambda name: User(
        id=data.get("id", ""),
        name=name,
        email=data.get("email"),
        age=data.get("age")
    )

    return (
        Some(data.get("id", ""))
        .filter(validate_id)
        .bind(lambda id: 
            Some(data.get("name", ""))
            .filter(validate_name)
            .map(build_user)
        )
    )

def get_user_contact(user: User) -> str:
    get_default = lambda name: f"No email for {name}"
    
    return (
        Option.from_optional(user.email)
        .default_value(get_default(user.name))
    )

# Usage
user_data = {
    "id": "1",
    "name": "Alice",
    "email": "alice@example.com",
    "age": 30
}

# DON'T ❌
def create_user_unsafe(data: dict) -> Opt[User]:
    if not data.get("id") or not data.get("name"):
        return None
    return User(
        id=data["id"],
        name=data["name"],
        email=data.get("email"),
        age=data.get("age")
    )

# WHY: Option provides cleaner validation and creation logic
```

## Testing Example

```python
def test_user_creation():
    # Valid data
    data = {"id": "1", "name": "Alice"}
    result = create_user(data)
    assert result.is_some()
    assert result.value.name == "Alice"
    
    # Invalid data
    invalid = {"name": "Alice"}  # Missing ID
    result = create_user(invalid)
    assert result.is_none()

def test_email_validation():
    # Valid email
    result = validate_email("test@example.com")
    assert result.is_some()
    
    # Invalid email
    result = validate_email("invalid-email")
    assert result.is_none()
