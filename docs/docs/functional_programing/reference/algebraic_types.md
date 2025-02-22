# Algebraic Types

## Overview
Algebraic types provide type-safe ways to represent complex data structures and handle various programming patterns in a functional way. The Expression library provides three main algebraic types:

- **Union**: For discriminated unions/sum types
- **Option**: For optional values
- **Result**: For computations that can fail

## Type Comparison

| Type | Use Case | Alternative To | Best For |
|------|-----------|---------------|-----------|
| Union | Variants of data | Inheritance/Enums | State machines, business rules |
| Option | Optional values | None/null checks | Safe nullable operations |
| Result | Error handling | Exceptions | Railway oriented programming |

## Union Types

### When to Use Union
✓ Representing variants of data
✓ Type-safe enums with data
✓ State machines
✓ Complex business rules
✓ Pattern matching

### Basic Union Example
```python
from expression import union

@union
class Shape:
    def Circle(radius: float): ...
    def Rectangle(width: float, height: float): ...
    def Square(side: float): ...

def area(shape: Shape) -> float:
    return shape.match(
        lambda Circle(r): math.pi * r * r,
        lambda Rectangle(w, h): w * h,
        lambda Square(s): s * s
    )
```

### State Machine Pattern
```python
@union
class TaskState:
    def Pending(): ...
    def Running(progress: float): ...
    def Complete(result: str): ...
    def Failed(error: str): ...

def process_task(state: TaskState) -> str:
    return state.match(
        lambda Pending(): "Waiting to start",
        lambda Running(p): f"Progress: {p*100:.0f}%",
        lambda Complete(r): f"Done: {r}",
        lambda Failed(e): f"Error: {e}"
    )
```

## Option Type

### When to Use Option
✓ Handling optional values
✓ Safe null-value operations
✓ Chaining optional computations
✓ Type-safe missing data

### Basic Option Example
```python
from expression import Option, Some, Nothing

def find_user(user_id: str) -> Option[dict]:
    users = {"1": {"name": "Alice"}}
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
```

## Result Type

### When to Use Result
✓ Error handling without exceptions
✓ Validation chains
✓ Railway oriented programming
✓ Operations that can fail
✓ Type-safe error handling

### Basic Result Example
```python
from expression import Result

def validate_age(age: int) -> Result[int, str]:
    return (Result.ok(age)
        .bind(lambda x: 
            Result.ok(x) if x >= 0 
            else Result.error("Age must be positive"))
        .bind(lambda x: 
            Result.ok(x) if x <= 150
            else Result.error("Age too high")))

def create_user(data: dict) -> Result[User, str]:
    return (
        validate_age(data.get("age", 0))
        .bind(lambda age:
            Result.ok(User(
                name=data.get("name", ""),
                age=age
            )) if data.get("name")
            else Result.error("Name is required")
        )
    )
```

## Integration Patterns

### Combining Different Types
```python
# Union with Option
@union
class ParseResult:
    def Integer(value: int): ...
    def Float(value: float): ...
    def String(value: str): ...

def safe_parse(s: str) -> Option[ParseResult]:
    return (Result.ok(s)
        .bind(lambda x: 
            Result.ok(ParseResult.Integer(int(x)))
            .map_error(lambda _: x))
        .bind(lambda x: 
            Result.ok(ParseResult.Float(float(x)))
            .map_error(lambda _: x))
        .map(lambda x: ParseResult.String(x))
        .to_option())
```

# Union with Result
@union
class ValidationError:
    def Missing(field: str): ...
    def Invalid(field: str, reason: str): ...
    def TooLong(field: str, max_length: int): ...

def validate(data: dict) -> Result[dict, ValidationError]:
    if 'name' not in data:
        return Result.error(ValidationError.Missing('name'))
    if len(data['name']) > 100:
        return Result.error(ValidationError.TooLong('name', 100))
    return Result.ok(data)

# Option with Result
def find_and_validate(id: str) -> Result[User, str]:
    return (find_user(id)
        .to_result(f"User {id} not found")
        .bind(validate_user))
```

### Practical Examples

### Form Validation
```python
def validate_form(data: dict) -> Result[dict, List[str]]:
    def validate_field(key: str, validator: Callable[[str], Result[Any, str]]) -> Option[Any]:
        return (Option.of_obj(data.get(key))
            .map(str)
            .bind(lambda x: Option.of_obj(validator(x).to_option())))
    
    email = validate_field("email", validate_email)
    name = validate_field("name", validate_name)
    age = validate_field("age", validate_age)
    
    def collect_errors() -> List[str]:
        return [err for err in [
            validate_email(data.get("email", "")),
            validate_name(data.get("name", "")),
            validate_age(data.get("age", ""))
        ] if err.is_error()]
    
    errors = collect_errors()
    if errors:
        return Result.error(errors)
        
    return Result.ok({
        "email": email.value,
        "name": name.value,
        "age": age.value
    })
```

### API Integration
```python
def fetch_api_data(url: str) -> Result[dict, str]:
    return (Result.ok(url)
        .bind(lambda u: 
            Result.ok(requests.get(u))
            .map_error(lambda e: f"Request failed: {e}"))
        .bind(lambda r:
            Result.ok(r.json())
            .map_error(lambda e: f"Invalid JSON: {e}")))
```

### Configuration Loading
```python
def load_yaml(content: str) -> Result[dict, str]:
    return (Result.ok(content)
        .bind(lambda c: 
            Result.ok(yaml.safe_load(c))
            .map_error(lambda e: f"Invalid YAML: {e}")))

def load_config(path: str) -> Result[dict, str]:
    return (Result.ok(path)
        .bind(lambda p: 
            Result.ok(open(p).read())
            .map_error(lambda e: f"Cannot read file: {e}"))
        .bind(load_yaml))
```

### Database Operations
```python
def execute_query(query: str, params: tuple) -> Result[List[tuple], str]:
    def run_query(conn: Connection) -> Result[List[tuple], str]:
        return (Result.ok(conn.cursor())
            .bind(lambda cur: 
                Result.ok(cur.execute(query, params))
                .bind(lambda _: Result.ok(cur.fetchall()))))
    
    return (Result.ok(connection())
        .bind(run_query)
        .map_error(lambda e: f"Database error: {e}"))
```

## Best Practices

### DO ✓
- Use pattern matching consistently
- Make matches exhaustive
- Chain operations
- Handle all cases explicitly
- Use appropriate type for each case
- Keep variants focused
- Document type choices

### DON'T ✗
- Mix with exceptions/null
- Skip variant cases
- Mutate variant data
- Use for simple cases
- Ignore type safety
- Create deep nesting
- Mix different patterns

## Performance Considerations

1. Pattern matching is optimized
2. Minimal overhead vs native types
3. Memory efficient implementations
4. Good for domain modeling
5. Chain operations efficiently

## Testing Strategies

### Unit Testing
```python
def test_algebraic_types():
    # Test Option
    assert find_user("1").is_some()
    assert find_user("invalid").is_none()
    
    # Test Result
    assert validate_age(25).is_ok()
    assert validate_age(-1).is_error()
    
    # Test Union
    task = TaskState.Running(0.5)
    assert "50%" in process_task(task)
```

### Property Testing
```python
@given(st.integers())
def test_type_properties(x: int):
    # Option laws
    opt = Option.some(x)
    assert opt.map(lambda x: x) == opt
    
    # Result laws
    res = Result.ok(x)
    assert res.map(lambda x: x) == res
    
    # Union properties
    state = TaskState.Running(x/100)
    assert "%" in process_task(state)