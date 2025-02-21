# Python Functional Programming Guide with Expression Library

## Core Principles

1. Immutability
2. Pure Functions
3. Function Composition
4. Type Safety

## Basic Functional Patterns

### Pure Functions and Immutability

```python
from expression.collections import Block, Map
from dataclasses import dataclass
from typing import Sequence

# DO ✅
@dataclass(frozen=True)
class Score:
    value: int
    subject: str

def calculate_average(scores: Block[Score]) -> float:
    extract_value = lambda s: s.value
    return scores.map(extract_value).average()

# Process data without mutations
def filter_high_scores(scores: Block[Score]) -> Block[Score]:
    is_high_score = lambda s: s.value >= 90
    return scores.filter(is_high_score)

# DON'T ❌
class MutableScore:
    def __init__(self, value: int, subject: str):
        self.value = value
        self.subject = subject

def update_scores(scores: list[MutableScore]) -> None:
    for score in scores:
        score.value += 5  # Mutation!

# WHY: Pure functions and immutable data prevent side effects
```

### Function Composition

```python
from expression.core import pipe, compose
from typing import Callable

# DO ✅
def normalize_string(s: str) -> str:
    return s.lower().strip()

def validate_length(s: str) -> bool:
    return 3 <= len(s) <= 50

def process_input(validate: Callable[[str], bool]) -> Callable[[str], str]:
    process_text = lambda s: s if validate(s) else ""
    
    def processor(text: str) -> str:
        return pipe(
            text,
            normalize_string,
            process_text
        )
    return processor

validate_name = process_input(validate_length)
assert validate_name("  John  ") == "john"

# DON'T ❌
def process_input_imperative(text: str) -> str:
    text = text.lower()
    text = text.strip()
    if not (3 <= len(text) <= 50):
        return ""
    return text

# WHY: Function composition creates reusable, testable pipelines
```

### Higher-Order Functions

```python
from typing import TypeVar, Callable
from expression import Option, Some, Nothing

T = TypeVar('T')
U = TypeVar('U')

# DO ✅
def safe_transform(f: Callable[[T], U]) -> Callable[[T], Option[U]]:
    def wrapper(x: T) -> Option[U]:
        try:
            return Some(f(x))
        except Exception:
            return Nothing
    return wrapper

safe_int = safe_transform(int)
assert safe_int("123").is_some()
assert safe_int("abc").is_none()

# DON'T ❌
def transform_with_default(x: str, default: int) -> int:
    try:
        return int(x)
    except ValueError:
        return default

# WHY: Higher-order functions make error handling more composable
```

## Advanced Patterns

### Railway-Oriented Programming

```python
from expression import Result, Success, Failure
from typing import Any

# DO ✅
def validate_age(age: Any) -> Result[int]:
    return (
        safe_transform(int)(age)
        .to_result("Invalid age format")
        .bind(lambda n: 
            Success(n) if 0 <= n <= 120
            else Failure("Age must be between 0 and 120")
        )
    )

def validate_name(name: Any) -> Result[str]:
    return (
        Some(str(name))
        .to_result("Invalid name")
        .bind(lambda n:
            Success(n) if n.strip()
            else Failure("Name cannot be empty")
        )
    )

# Create validated user
def create_validated_user(data: dict) -> Result[dict]:
    return (
        validate_name(data.get("name"))
        .bind(lambda name:
            validate_age(data.get("age"))
            .map(lambda age: {"name": name, "age": age})
        )
    )

# DON'T ❌
def create_user_unsafe(data: dict) -> dict:
    if "name" not in data or not data["name"].strip():
        raise ValueError("Invalid name")
    if "age" not in data:
        raise ValueError("Missing age")
    try:
        age = int(data["age"])
        if not (0 <= age <= 120):
            raise ValueError("Invalid age range")
    except ValueError:
        raise ValueError("Invalid age format")
    return {"name": data["name"], "age": age}

# WHY: Railway-oriented programming makes error handling explicit and composable
```

## Best Practices

### DO ✅
- Use frozen dataclasses for data structures
- Compose functions with pipe and compose
- Handle errors with Option and Result
- Use type hints consistently
- Write small, focused functions

### DON'T ❌
- Mutate data structures
- Use exceptions for control flow
- Write functions with side effects
- Mix functional and imperative styles
- Create complex class hierarchies

## Testing Example

```python
from expression.collections import Block

def test_score_processing():
    # Given
    scores = Block.of_seq([
        Score(95, "Math"),
        Score(85, "English"),
        Score(92, "Science")
    ])
    
    # When
    check_high_score = lambda score: score >= 90
    high_scores = filter_high_scores(scores)
    avg = calculate_average(scores)
    
    # Then
    assert len(high_scores) == 2
    assert 90 <= avg <= 91

def test_input_processing():
    processor = process_input(validate_length)
    
    assert processor("  TEST  ") == "test"
    assert processor("a") == ""  # Too short
    assert processor("  ") == ""  # Empty after normalization

def test_validated_user():
    # Valid data
    good_data = {"name": "John", "age": "25"}
    result = create_validated_user(good_data)
    assert result.is_success()
    
    # Invalid data
    bad_data = {"name": "", "age": "invalid"}
    result = create_validated_user(bad_data)
    assert result.is_failure()
