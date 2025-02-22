# Union

## Contents
1. [Overview](#overview)
2. [Type Comparison](#type-comparison)
3. [API Reference](#api-reference)
   - [Creation Methods](#creation-methods)
   - [Pattern Methods](#pattern-methods)
   - [Utility Methods](#utility-methods)
4. [Common Patterns](#common-patterns)
5. [Integration Patterns](#integration-patterns)
6. [Best Practices](#best-practices)
7. [Testing Patterns](#testing-patterns)
8. [Recipes](#recipes)

## Overview
Union types (discriminated unions) provide type-safe representation of values that can be one of several variants. They enable pattern matching and exhaustive checking of all possible cases.

## Type Comparison
| Type | Purpose | Alternative To | Best For |
|------|---------|---------------|-----------|
| Union | Variant types | Enums/inheritance | State machines, domain models |
| Option | Optional values | None/null | Missing data |
| Result | Error handling | Exceptions | Operation failures |

## API Reference

### Creation Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `@union` | Type decorator | `@union class Shape` | [Common Patterns](#basic-types) |
| `def Variant()` | Define variant | `def Circle(radius: float)` | [Pattern Methods](#pattern-matching) |
| `Variant(...)` | Create instance | `Shape.Circle(5.0)` | [Common Patterns](#state-machines) |

### Pattern Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `match()` | Pattern match | `shape.match(...)` | [Best Practices](#do-) |
| `is_circle()` | Type check | `shape.is_circle()` | [Best Practices](#dont-) |
| `circle` | Unsafe access | `shape.circle  # Can raise` | [Best Practices](#dont-) |

### Utility Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `map()` | Transform variant | `shape.map(transform)` | [Integration Patterns](#with-collections) |
| `bind()` | Chain unions | `state.bind(transition)` | [Common Patterns](#state-machines) |
| `iter()` | Iterate values | `shape.iter()` | [Integration Patterns](#with-collections) |

## Common Patterns

### Basic Types
```python
from expression import union

@union
class Shape:
    def Circle(radius: float): ...
    def Rectangle(width: float, height: float): ...
    def Square(side: float): ...

def area(shape: Shape) -> float:
    """Calculate area using pattern matching."""
    return shape.match(
        lambda Circle(r): math.pi * r * r,
        lambda Rectangle(w, h): w * h,
        lambda Square(s): s * s
    )
```

### State Machines
```python
@union
class TaskState:
    def Pending(): ...
    def Running(progress: float): ...
    def Complete(result: str): ...
    def Failed(error: str): ...

def process_task(state: TaskState) -> str:
    """Handle task states with exhaustive matching."""
    return state.match(
        lambda Pending(): "Waiting to start",
        lambda Running(p): f"Progress: {p*100:.0f}%",
        lambda Complete(r): f"Done: {r}",
        lambda Failed(e): f"Error: {e}"
    )

def transition(state: TaskState, 
               event: Event) -> TaskState:
    """Type-safe state transitions."""
    return state.match(
        lambda Pending(): 
            TaskState.Running(0.0) if event.is_start()
            else state,
        lambda Running(p):
            TaskState.Complete("Done") if p >= 1.0
            else TaskState.Running(p + 0.1),
        lambda Complete(_): state,
        lambda Failed(_): state
    )
```

### Domain Modeling
```python
@union
class User:
    def Anonymous(): ...
    def Registered(id: str, name: str): ...
    def Admin(id: str, name: str, level: int): ...

@union
class Permission:
    def Allow(resource: str): ...
    def Deny(reason: str): ...

def check_access(user: User, 
                resource: str) -> Permission:
    """Model domain rules with unions."""
    return user.match(
        lambda Anonymous(): 
            Permission.Deny("Login required"),
        lambda Registered(_, _): 
            Permission.Allow(resource)
            if is_public(resource)
            else Permission.Deny("Admin required"),
        lambda Admin(_, _, level):
            Permission.Allow(resource)
            if level >= required_level(resource)
            else Permission.Deny("Insufficient privileges")
    )
```

## Integration Patterns

### With Collections
```python
def process_shapes(shapes: Block[Shape]) -> Block[float]:
    """Process collection of union types."""
    return shapes.map(area)

def filter_circles(shapes: Block[Shape]) -> Block[float]:
    """Filter specific variants."""
    return shapes.choose(lambda s: 
        Option.some(s.circle.radius)
        if s.is_circle()
        else Option.none())
```

### With Option/Result
```python
def parse_shape(data: dict) -> Option[Shape]:
    """Safe union type creation."""
    return (Option.of_obj(data.get("type"))
        .match(
            lambda t: match_shape_type(t, data),
            lambda: Option.none()
        ))

def validate_shape(shape: Shape) -> Result[Shape, str]:
    """Validate union type values."""
    return shape.match(
        lambda Circle(r): 
            Result.ok(shape) if r > 0
            else Result.error("Invalid radius"),
        lambda Rectangle(w, h):
            Result.ok(shape) if w > 0 and h > 0
            else Result.error("Invalid dimensions"),
        lambda Square(s):
            Result.ok(shape) if s > 0
            else Result.error("Invalid side")
    )
```

### With State Management
```python
@dataclass(frozen=True)
class StateMachine[S]:
    current: S
    history: Block[S] = Block.empty()

def apply_transition[S](
    machine: StateMachine[S],
    event: Event
) -> StateMachine[S]:
    """Manage union type state transitions."""
    new_state = transition(machine.current, event)
    return StateMachine(
        current=new_state,
        history=machine.history.cons(machine.current)
    )
```

## Best Practices

### DO ✓
- Use pattern matching consistently
- Make matches exhaustive
- Model domain concepts
- Keep variants focused
- Document type choices
- Use type hints
- Handle all cases

### DON'T ✗
- Access variants directly
- Mix with inheritance
- Skip variant cases
- Create deep nesting
- Use for simple flags
- Ignore type safety
- Leave matches incomplete

## Testing Patterns

### Unit Tests
```python
def test_union_types():
    """Test union type operations."""
    # Test creation
    circle = Shape.Circle(5.0)
    assert circle.is_circle()
    
    # Test pattern matching
    result = circle.match(
        lambda Circle(r): r * 2,
        lambda Rectangle(w, h): w + h,
        lambda Square(s): s
    )
    assert result == 10.0
    
    # Test exhaustiveness
    def incomplete_match(s: Shape) -> float:
        return s.match(
            lambda Circle(r): r
            # Error: Missing Rectangle and Square
        )
```

### Property Tests
```python
@given(st.floats(min_value=0, max_value=100))
def test_shape_properties(x: float):
    """Test union type properties."""
    shape = Shape.Circle(x)
    
    # Identity
    assert shape.match(
        lambda Circle(r): Shape.Circle(r),
        lambda Rectangle(w, h): shape,
        lambda Square(s): shape
    ) == shape
    
    # Pattern matching coverage
    handled = False
    shape.match(
        lambda Circle(_): handled := True,
        lambda Rectangle(_, _): None,
        lambda Square(_): None
    )
    assert handled
```

## Recipes

### Visitor Pattern
```python
@union
class Expr:
    def Number(value: float): ...
    def Add(left: 'Expr', right: 'Expr'): ...
    def Mul(left: 'Expr', right: 'Expr'): ...

class ExprVisitor(Protocol[T]):
    def visit_number(self, value: float) -> T: ...
    def visit_add(self, left: 'Expr', right: 'Expr') -> T: ...
    def visit_mul(self, left: 'Expr', right: 'Expr') -> T: ...

def accept[T](expr: Expr, visitor: ExprVisitor[T]) -> T:
    """Implement visitor pattern with unions."""
    return expr.match(
        lambda Number(v): visitor.visit_number(v),
        lambda Add(l, r): visitor.visit_add(l, r),
        lambda Mul(l, r): visitor.visit_mul(l, r)
    )
```

### Command Pattern
```python
@union
class Command:
    def Add(item: str): ...
    def Remove(item: str): ...
    def Clear(): ...

class CommandHandler:
    def __init__(self):
        self.items = Block.empty()
    
    def handle(self, cmd: Command) -> Result[Block[str], str]:
        """Handle commands using pattern matching."""
        return cmd.match(
            lambda Add(item): 
                Result.ok(self.items.cons(item)),
            lambda Remove(item):
                Result.ok(self.items.filter(
                    lambda x: x != item)),
            lambda Clear():
                Result.ok(Block.empty())
        )
```

### Strategy Pattern
```python
@union
class SortStrategy:
    def Quick(): ...
    def Merge(): ...
    def Insertion(): ...

def sort[T](items: Block[T], 
            strategy: SortStrategy) -> Block[T]:
    """Implement strategy pattern with unions."""
    return strategy.match(
        lambda Quick(): quick_sort(items),
        lambda Merge(): merge_sort(items),
        lambda Insertion(): insertion_sort(items)
    )
```