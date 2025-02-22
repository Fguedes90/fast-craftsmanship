# Option

## Contents
1. [Overview](#overview)
2. [Type Comparison](#type-comparison)
3. [API Reference](#api-reference)
   - [Creation Methods](#creation-methods)
   - [Transform Methods](#transform-methods)
   - [Access Methods](#access-methods)
4. [Common Patterns](#common-patterns)
5. [Integration Patterns](#integration-patterns)
6. [Best Practices](#best-practices)
7. [Testing Patterns](#testing-patterns)
8. [Recipes](#recipes)

## Overview
Option represents optional values in a type-safe way. It eliminates null checks by making missing values explicit and providing functional transformation methods.

## Type Comparison
| Type | Purpose | Alternative To | Best For |
|------|---------|---------------|-----------|
| Option | Optional values | Null checks | Safe nullable operations |
| Result | Error handling | Exceptions | Operations that can fail |
| Union | Variant types | Enums/inheritance | State machines |

## API Reference

### Creation Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `some(x)` | Create Some | `Option.some(42)` | [Common Patterns](#safe-computations) |
| `none()` | Create None | `Option.none()` | [Best Practices](#do-) |
| `of_obj(x)` | From nullable | `Option.of_obj(maybe_none)` | [Integration Patterns](#with-collections) |
| `from_optional(x)` | From Optional | `Option.from_optional(obj.field)` | [Recipes](#nullable-interop) |

### Transform Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `map(f)` | Transform value | `opt.map(str)` | [Common Patterns](#safe-computations) |
| `bind(f)` | Chain Options | `opt.bind(safe_sqrt)` | [Best Practices](#do-) |
| `filter(p)` | Keep if matches | `opt.filter(is_valid)` | [Integration Patterns](#with-collections) |
| `map_or(f, d)` | Transform with default | `opt.map_or(str, "none")` | [Recipes](#default-handling) |

### Access Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `match(some,none)` | Pattern match | `opt.match(str, lambda: "none")` | [Best Practices](#do-) |
| `default_value(x)` | Get or default | `opt.default_value(0)` | [Common Patterns](#safe-computations) |
| `value` | Unsafe get | `opt.value  # Can raise` | [Best Practices](#dont-) |
| `is_some/is_none` | Check state | `opt.is_some()` | [Best Practices](#dont-) |

## Common Patterns

### Safe Computations
```python
def safe_divide(x: float, y: float) -> Option[float]:
    """Safe division without exceptions."""
    return Option.some(x / y) if y != 0 else Option.none()

def safe_sqrt(x: float) -> Option[float]:
    """Safe square root without exceptions."""
    return Option.some(x ** 0.5) if x >= 0 else Option.none()

# Chain operations safely
def compute(x: float) -> Option[float]:
    return (Option.some(x)
        .bind(lambda n: safe_divide(n, 2))  # Half
        .bind(safe_sqrt))                   # Square root
```

### Dictionary Access
```python
def get_nested(data: dict, *keys: str) -> Option[Any]:
    """Safely access nested dictionary keys."""
    def get_key(d: Option[dict], k: str) -> Option[Any]:
        return d.bind(lambda x: Option.of_obj(x.get(k)))
    
    return functools.reduce(get_key, keys, Option.some(data))

# Usage example
config = {"db": {"host": "localhost"}}
port = get_nested(config, "db", "port").default_value(5432)
```

### Collection Operations
```python
def first_matching[T](
    pred: Callable[[T], bool], 
    xs: Iterable[T]
) -> Option[T]:
    """Find first item matching predicate."""
    return next(
        (Option.some(x) for x in xs if pred(x)), 
        Option.none()
    )

def extract_values[T](
    items: Block[Option[T]]
) -> Block[T]:
    """Extract valid values from collection."""
    return items.choose(lambda x: x)
```

## Integration Patterns

### With Result
```python
def parse_config(data: Option[str]) -> Result[dict, str]:
    """Convert Option to Result with error message."""
    return data.match(
        lambda x: parse_json(x),
        lambda: Result.error("No config data")
    )

def find_user(id: str) -> Option[User]:
    """Convert Result to Option."""
    return fetch_user(id).to_option()
```

### With Collections
```python
from expression.collections import Block, Seq, Map

def process_items(items: Block[str]) -> Option[float]:
    """Process collection with Option chain."""
    return (items
        .try_head()           # Get first safely
        .bind(safe_parse)     # Try parse
        .bind(safe_sqrt))     # Try sqrt

def collect_values[K,V](m: Map[K, Option[V]]) -> Map[K, V]:
    """Filter map keeping only Some values."""
    return m.filter(lambda _, v: v.is_some())
        .map(lambda k, v: v.value)

def process_stream(xs: Seq[str]) -> Seq[int]:
    """Process stream keeping valid values."""
    return xs.choose(safe_parse_int)
```

### With Nullables
```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: Optional[str] = None
    age: Optional[int] = None

def get_user_contact(user: User) -> str:
    """Handle Optional fields with Option."""
    return (Option.from_optional(user.email)
        .default_value(f"No email for {user.name}"))
```

## Best Practices

### DO ✓
- Use pattern matching consistently
- Chain transformations fluently
- Handle both Some/None cases
- Return early with none()
- Keep functions pure
- Document Option returns
- Use type hints

### DON'T ✗
- Access value directly
- Mix with None checks
- Ignore None cases
- Raise exceptions
- Use for errors
- Nest Options deeply
- Check is_some/is_none

## Testing Patterns

### Unit Tests
```python
def test_option_operations():
    """Test Option operations."""
    # Creation and transformation
    assert Option.some(42).map(str).value == "42"
    assert Option.none().map(str).is_none()
    
    # Pattern matching
    result = Option.some(42).match(
        lambda x: f"Got {x}",
        lambda: "Nothing"
    )
    assert result == "Got 42"
    
    # Chaining
    def safe_div(x: int) -> Option[float]:
        return Option.some(1/x) if x != 0 else Option.none()
    
    assert Option.some(2).bind(safe_div).value == 0.5
    assert Option.some(0).bind(safe_div).is_none()
```

### Property Tests
```python
@given(st.integers())
def test_option_laws(x: int):
    """Test Option monad laws."""
    # Identity
    opt = Option.some(x)
    assert opt.map(lambda x: x) == opt
    
    # Composition
    f = lambda x: x * 2
    g = lambda x: x + 1
    
    # Left identity
    assert Option.some(x).bind(f) == f(x)
    
    # Right identity
    assert opt.bind(Option.some) == opt
    
    # Associativity
    assert (opt.map(f).map(g) == 
            opt.map(lambda x: g(f(x))))
```

## Recipes

### Nullable Interop
```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    host: str
    port: Optional[int] = None
    timeout: Optional[float] = None

def validate_config(cfg: Config) -> Option[Config]:
    """Validate optional fields."""
    return (Option.from_optional(cfg.port)
        .map_or(lambda p: p, 5432)
        .filter(lambda p: 0 < p < 65536)
        .map(lambda p: Config(
            host=cfg.host,
            port=p,
            timeout=cfg.timeout
        )))
```

### Default Handling
```python
def with_default[T](
    opt: Option[T],
    default: Callable[[], T]
) -> T:
    """Lazy default value evaluation."""
    return opt.match(
        lambda x: x,
        default
    )

# Usage example
result = with_default(
    Option.none(),
    lambda: expensive_computation()
)
```

### Validation Chain
```python
def validate_user(data: dict) -> Option[User]:
    """Validate user data with Option chain."""
    def validate_email(email: str) -> Option[str]:
        return Option.some(email) if "@" in email else Option.none()
    
    def validate_age(age: int) -> Option[int]:
        return Option.some(age) if 0 <= age <= 150 else Option.none()
    
    return (Option.of_obj(data.get("name"))
        .filter(bool)
        .bind(lambda name:
            Option.of_obj(data.get("email"))
            .bind(validate_email)
            .bind(lambda email:
                Option.of_obj(data.get("age"))
                .bind(validate_age)
                .map(lambda age: User(
                    name=name,
                    email=email,
                    age=age
                )))))
```

### Collection Processing
```python
def process_values[T,R](
    items: Block[dict],
    key: str,
    transform: Callable[[T], Option[R]]
) -> Block[R]:
    """Process collection of dictionaries safely."""
    return (items
        .map(lambda x: Option.of_obj(x.get(key)))
        .filter(Option.is_some)
        .map(lambda x: x.value)
        .choose(transform))

# Usage example
users = Block.of_seq([
    {"name": "Alice", "age": "30"},
    {"name": "Bob", "age": "invalid"},
    {"name": "Charlie", "age": "25"}
])

ages = process_values(users, "age", safe_parse_int)
assert list(ages) == [30, 25]