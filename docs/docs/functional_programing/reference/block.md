# Block

## Contents
1. [Overview](#overview)
2. [Quick Selection Guide](#quick-selection-guide)
3. [API Reference](#api-reference)
   - [Creation Methods](#creation-methods)
   - [Access Methods](#access-methods)
   - [Transform Methods](#transform-methods)
   - [Combine Methods](#combine-methods)
   - [Slice Methods](#slice-methods)
   - [Sort Methods](#sort-methods)
4. [Performance Characteristics](#performance-characteristics)
5. [Common Patterns](#common-patterns)
6. [Integration Patterns](#integration-patterns)
7. [Best Practices](#best-practices)
8. [Testing Patterns](#testing-patterns)
9. [Type Safety](#type-safety)
10. [Recipes](#recipes)

## Overview
A high-performance, immutable sequence implementation optimized for functional programming. Key features:
- Immutable data structure (see [Performance Characteristics](#performance-characteristics))
- Type-safe operations (see [Type Safety](#type-safety))
- Thread-safe by design (see [Integration Patterns](#integration-patterns))
- Efficient prepend operations (see [Common Patterns](#common-patterns))

## Quick Selection Guide

### When to Use Block
✓ Immutable operations needed
✓ Thread safety required
✓ Fast prepend operations
✓ Type safety important
✓ Small to medium collections

### When to Use Alternatives
| Need | Use Instead |
|------|-------------|
| Lazy evaluation | Seq |
| Key-value pairs | Map |
| Large datasets | Seq |
| Mutable operations | List |
| Simple indexing | Tuple |

## API Reference

### Creation Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `empty()` | Empty block | `Block.empty()` | [Collection Building](#collection-building) |
| `of(*args)` | From values | `Block.of(1,2,3)` | [Unit Tests](#unit-tests) |
| `of_seq(xs)` | From iterable | `Block.of_seq(range(3))` | [Integration Patterns](#with-other-collections) |
| `unfold(s,g)` | Generate sequence | `Block.unfold(0, next_val)` | [Common Patterns](#common-patterns) |

### Access Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `head()` | First item | `xs.head()` | [Error Handling](#error-handling) |
| `try_head()` | Safe first | `xs.try_head().map(str)` | [Option/Result Integration](#with-optionresult) |
| `tail()` | All but first | `xs.tail()` | [Collection Building](#collection-building) |
| `item(i)` | Index access | `xs.item(0)` | [Best Practices](#best-practices) |

### Transform Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `map(f)` | Transform all | `xs.map(str)` | [Performance Characteristics](#operation-complexity) |
| `filter(p)` | Keep matching | `xs.filter(bool)` | [Common Patterns](#safe-data-processing) |
| `choose(f)` | Filter+map | `xs.choose(safe_parse)` | [Error Handling](#error-handling) |
| `collect(f)` | Flat map | `xs.collect(expand)` | [Integration Patterns](#with-other-collections) |

### Combine Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `fold(f,s)` | Accumulate | `xs.fold(add, 0)` | [Common Patterns](#common-patterns) |
| `partition(p)` | Split by pred | `xs.partition(is_even)` | [Testing Patterns](#property-tests) |
| `zip(ys)` | Pair elements | `xs.zip(ys)` | [Type Safety](#generic-parameters) |
| `concat(srcs)` | Join blocks | `Block.concat([xs,ys])` | [Collection Building](#collection-building) |

### Slice Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `take(n)` | First n | `xs.take(5)` | [Performance Characteristics](#memory-usage) |
| `skip(n)` | Drop first n | `xs.skip(5)` | [Common Patterns](#collection-building) |
| `take_last(n)` | Last n | `xs.take_last(5)` | [Best Practices](#best-practices) |
| `skip_last(n)` | Drop last n | `xs.skip_last(5)` | [Best Practices](#best-practices) |

### Sort Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `sort()` | Sort elements | `xs.sort()` | [Performance Characteristics](#operation-complexity) |
| `sort_with(f)` | Sort by key | `xs.sort_with(len)` | [Common Patterns](#safe-data-processing) |

## Performance Characteristics

### Operation Complexity
| Operation | Complexity | Note |
|-----------|------------|------|
| Prepend (cons) | O(1) | Optimal for building |
| Access | O(1) | Index lookup |
| Map/Filter | O(n) | Single pass |
| Sort | O(n log n) | New instance |

### Memory Usage
- Immutable references
- Shared structure optimization
- Each operation creates new block
- Memory freed when unreferenced

## Common Patterns

### Safe Data Processing
```python
def process_data(items: Block[str]) -> Option[int]:
    return (items
        .filter(str.strip)                # Remove empty
        .map(str.lower)                   # Normalize
        .try_head()                       # Safely get first
        .bind(safe_parse_int)             # Try convert
        .filter(lambda x: x > 0))         # Validate
```

### Error Handling
```python
def validate_items(items: Block[str]) -> Result[Block[int], str]:
    return (Result.ok(items)
        .map(lambda xs: xs.filter(bool))
        .map(lambda xs: xs.map(safe_parse_int))
        .bind(Result.sequence))

def safe_parse_int(s: str) -> Result[int, str]:
    return (Result.ok(s)
        .map(str.strip)
        .filter(bool)
        .bind(lambda x: 
            Result.ok(int(x))
            .map_error(lambda _: f"Invalid integer: {x}")))
```

### Collection Building
```python
from functools import reduce
from typing import TypeVar, Callable

T = TypeVar('T')
R = TypeVar('R')

def build_block[T](xs: Iterable[T]) -> Block[T]:
    """Build block efficiently using cons."""
    return reduce(
        lambda acc, x: acc.cons(x),
        reversed(xs),  # Reverse to maintain order
        Block.empty()
    )

def transform_chain[T,R](items: Block[T], 
                        f: Callable[[T], R]) -> Block[R]:
    """Efficient transformation chain."""
    return (items
        .filter(bool)          # Early filtering
        .map(f)               # Single pass transform
        .choose(safe_parse))  # Safe conversion
```

### Data Processing Pipeline
```python
from typing import TypeVar
from expression import Result, Option, pipe

T = TypeVar('T')
R = TypeVar('R')

def process_data[T,R](items: Block[T]) -> Result[Block[R], str]:
    """Common data processing pipeline pattern."""
    validate = lambda x: Result.ok(x).filter(bool)
    
    return (Result.ok(items)
        .map(lambda xs: xs
            .filter(bool)          # Remove empty/None
            .map(clean_data)       # Clean data
            .choose(safe_parse))   # Safe conversion
        .bind(validate_all))       # Validate results

# Usage example
def process_log_entries(lines: Block[str]) -> Result[Block[dict], str]:
    return process_data(lines)
        .map(lambda xs: xs.map(parse_json))
        .bind(Result.sequence)
```

### Resource Management
```python
from contextlib import contextmanager
from typing import Iterator, Any

@contextmanager
def with_resources[T](resources: Block[Any]) -> Iterator[Result[Block[T], str]]:
    """Safe resource management pattern."""
    try:
        yield (Result.ok(resources)
            .bind(initialize_all)
            .map(lambda rs: rs.map(setup)))
    finally:
        cleanup_all(resources)

# Usage example
def process_files(paths: Block[str]) -> Result[Block[str], str]:
    with with_resources(paths) as result:
        return result.bind(lambda files: 
            Result.traverse(files, process_one))
```

### State Machine
```python
from dataclasses import dataclass
from typing import Generic

@dataclass(frozen=True)
class State(Generic[T]):
    value: T
    history: Block[T] = Block.empty()

def state_transition[T](
    current: State[T], 
    transform: Callable[[T], Result[T, str]]
) -> Result[State[T], str]:
    """Type-safe state machine pattern."""
    return (Result.ok(current.value)
        .bind(transform)
        .map(lambda new_value: State(
            value=new_value,
            history=current.history.cons(current.value)
        )))
```

## Integration Patterns

### With Option/Result
```python
def find_first_valid(items: Block[str]) -> Option[str]:
    return (items
        .filter(bool)
        .try_head())

def process_all(items: Block[T]) -> Result[Block[R], str]:
    return Result.traverse(items, safe_transform)
```

### With Other Collections
```python
def to_map(items: Block[tuple[K, V]]) -> Map[K, V]:
    return Map.of_seq(items)

def to_seq(items: Block[T]) -> Seq[T]:
    return seq(items)
```

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_map(items: Block[T], 
                f: Callable[[T], R],
                max_workers: int = 4) -> Block[R]:
    """Thread-safe parallel mapping."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return Block.of_seq(executor.map(f, items))
```

### With Option/Result
```python
def safe_operations[T](items: Block[T]) -> Block[Result[R, str]]:
    """Integration with Option/Result types."""
    return (items
        .map(validate_item)    # Returns Option[T]
        .choose(lambda o:      # Convert Option to Result
            o.to_result("Invalid item"))
        .map(transform_item))  # Process valid items

def collect_results[T](
    results: Block[Result[T, str]]
) -> Result[Block[T], list[str]]:
    """Aggregate success/failure results."""
    successes = results.choose(lambda r: r.to_option())
    errors = results.choose(lambda r: 
        Option.some(r.error) if r.is_error() else Option.none())
    
    return (Result.ok(successes) if not errors
            else Result.error(list(errors)))
```

### With Collections
```python
def collection_transforms[T,R](items: Block[T]) -> Map[str, Seq[R]]:
    """Integration with other collection types."""
    return (items
        .map(transform)            # Transform items
        .group_by(get_category)    # Group into Map
        .map(lambda k, v:          # Convert values to Seq
            (k, seq(v))))          # for lazy processing

# Usage example
def process_logs(entries: Block[dict]) -> Map[str, Seq[dict]]:
    return collection_transforms(entries)
        .map(lambda k, v: 
            (k, v.filter(is_valid)
              .map(enrich_data)))
```

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor
from functools import partial

def parallel_transform[T,R](
    items: Block[T],
    f: Callable[[T], Result[R, str]],
    chunk_size: int = 100,
    max_workers: int = 4
) -> Result[Block[R], list[str]]:
    """Safe parallel processing pattern."""
    
    # Split into chunks for batch processing
    chunks = range(0, len(items), chunk_size)
    batches = [items.skip(i).take(chunk_size) for i in chunks]
    
    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = Block.of_seq(
            executor.map(partial(process_chunk, f), batches))
        
    # Combine results
    return collect_results(results).map(
        lambda xs: xs.collect(lambda x: x))

def process_chunk[T,R](
    f: Callable[[T], Result[R, str]],
    chunk: Block[T]
) -> Result[Block[R], str]:
    """Process a single chunk of items."""
    return Result.traverse(chunk, f)
```

## Best Practices

### DO ✓
- Use cons for building
- Chain transformations
- Handle empty cases
- Use type hints
- Document complex chains

### DON'T ✗
- Create unnecessary intermediates 
- Ignore Option/Result integration
- Mix mutable/immutable operations
- Use for huge datasets
- Nest transformations deeply

### Performance Optimization
```python
def optimize_pipeline[T,R](items: Block[T]) -> Block[R]:
    """Performance optimization patterns."""
    return (items
        .filter(is_valid)     # Filter early
        .map(transform)       # Single pass transform
        .take(10)            # Limit results early
        .map(finalize))      # Final transformation

def batch_process[T](
    items: Block[T], 
    batch_size: int
) -> Block[Result[R, str]]:
    """Efficient batch processing."""
    return (items
        .chunk(batch_size)          # Split into batches
        .map(process_batch)         # Process each batch
        .collect(lambda x: x))      # Flatten results
```

## Testing Patterns

### Unit Testing
```python
from expression import Result, Option
from typing import TypeVar, Callable

T = TypeVar('T')
R = TypeVar('R')

class TestBlock:
    def test_immutability(self):
        """Test immutability guarantees."""
        items = Block.of(1, 2, 3)
        transformed = items.map(lambda x: x * 2)
        
        assert items != transformed
        assert list(items) == [1, 2, 3]
        assert list(transformed) == [2, 4, 6]
    
    def test_error_handling(self):
        """Test error handling patterns."""
        empty = Block.empty()
        items = Block.of(1, 2, 3)
        
        # Option integration
        assert empty.try_head().is_none()
        assert items.try_head().contains(1)
        
        # Result integration
        to_str = lambda x: Result.ok(str(x))
        assert items.map(to_str).fold(
            lambda acc, r: acc.bind(
                lambda xs: r.map(lambda x: xs.cons(x))),
            Result.ok(Block.empty())
        ).is_ok()
    
    def test_transformations(self):
        """Test transformation chains."""
        items = Block.of("1", "2", "", "3", "invalid")
        
        result = (items
            .filter(bool)                  # Remove empty
            .choose(safe_parse_int)        # Convert to int
            .filter(lambda x: x > 1))      # Filter values
            
        assert list(result) == [2, 3]
```

### Property Testing
```python
from hypothesis import given, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule
from typing import List

class BlockProperties(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.items: List[int] = []
        self.block = Block.empty()
    
    @rule(x=st.integers())
    def add_item(self, x: int):
        """Adding items preserves order and content."""
        self.items.append(x)
        self.block = self.block.cons(x)
        
        assert list(reversed(self.block)) == self.items
    
    @rule(data=st.data())
    def slice_block(self, data):
        """Slicing operations preserve content."""
        if not self.items:
            return
            
        n = data.draw(st.integers(0, len(self.items)))
        taken = self.block.take(n)
        skipped = self.block.skip(n)
        
        assert list(reversed(taken)) == self.items[:n]
        assert list(reversed(skipped)) == self.items[n:]
    
    @rule()
    def transform_block(self):
        """Transformations preserve structure."""
        mapped = self.block.map(str)
        filtered = self.block.filter(lambda x: x % 2 == 0)
        
        assert len(mapped) == len(self.block)
        assert all(isinstance(x, str) for x in mapped)
        assert all(x % 2 == 0 for x in filtered)

@given(st.lists(st.integers()))
def test_block_construction(xs: list[int]):
    """Test block construction properties."""
    block = Block.of_seq(xs)
    
    assert len(block) == len(xs)
    assert list(block) == xs
    assert block.fold(lambda acc, x: acc + [x], []) == xs
```

## Troubleshooting

### Common Issues and Solutions

#### Memory Usage
```python
# Problem: High memory usage with large datasets
items = Block.of_seq(range(1_000_000))  # Creates large block
result = items.map(expensive_function)   # Doubles memory usage

# Solution: Use Seq for large datasets
from expression import seq
items = seq(range(1_000_000))           # Lazy sequence
result = items.map(expensive_function)   # Minimal memory
```

#### Type Safety
```python
# Problem: Mixed types in block
items = Block.of(1, "2", 3.0)  # Mixed types
result = items.map(lambda x: x + 1)  # TypeError

# Solution: Use type hints and validation
T = TypeVar('T', int, float)
def process_numbers[T](items: Block[T]) -> Block[T]:
    return items.map(lambda x: x + 1)

# Or validate at runtime
def ensure_numeric(items: Block[Any]) -> Block[float]:
    return items.choose(lambda x: 
        Option.some(float(x)) if isinstance(x, (int, float, str))
        else Option.none())
```

#### Performance
```python
# Problem: Inefficient block building
result = Block.empty()
for x in range(1000):
    result = Block.of_seq([*result, x])  # O(n²) complexity

# Solution: Use cons for building
from functools import reduce
result = reduce(
    lambda acc, x: acc.cons(x),
    range(999, -1, -1),  # Reverse range
    Block.empty()
)
```

#### Error Handling
```python
# Problem: Unsafe operations
def process(items: Block[str]) -> Block[int]:
    return items.map(int)  # Can raise ValueError

# Solution: Use Option/Result
def safe_process(items: Block[str]) -> Result[Block[int], str]:
    return Result.traverse(items, lambda s:
        Result.ok(s)
        .map(str.strip)
        .filter(bool)
        .bind(lambda x: 
            Result.ok(int(x))
            .map_error(lambda _: f"Invalid number: {x}")
        ))
```

### Performance Optimization Guide

1. **Building Collections**
   - Use `cons()` for building blocks forward
   - Batch operations when possible
   - Consider using Seq for large datasets

2. **Transformation Chains**
   - Filter early to reduce processing
   - Combine transformations when possible
   - Use `choose()` instead of `filter()` + `map()`

3. **Memory Management**
   - Release references to large blocks
   - Process in chunks for large datasets
   - Use lazy evaluation with Seq when appropriate

4. **Concurrency**
   - Use immutable blocks for thread safety
   - Process large datasets in parallel
   - Batch parallel operations appropriately


## Recipes

### Data Validation
```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar('T')
E = TypeVar('E')

@dataclass(frozen=True)
class Validation(Generic[T, E]):
    value: T
    errors: Block[E]

def validate_data[T, E](
    items: Block[T], 
    validators: Block[Callable[[T], Option[E]]]
) -> Validation[Block[T], E]:
    """Validate items collecting all errors."""
    def validate_item(item: T) -> Block[E]:
        return validators.choose(lambda v: v(item))
    
    errors = items.collect(validate_item)
    return Validation(items, errors)

# Usage example
def validate_user(user: dict) -> Option[str]:
    return (Option.some("Invalid email")
        if not is_valid_email(user.get("email"))
        else Option.none())

def validate_age(user: dict) -> Option[str]:
    return (Option.some("Invalid age")
        if not (0 <= user.get("age", -1) <= 120)
        else Option.none())

users = Block.of(
    {"email": "valid@email.com", "age": 25},
    {"email": "invalid", "age": 150}
)
validators = Block.of(validate_user, validate_age)
result = validate_data(users, validators)
```

### Data Transformation Pipeline
```python
def transform_pipeline[T, R](
    items: Block[T],
    transformers: Block[Callable[[T], Result[R, str]]]
) -> Result[Block[R], Block[str]]:
    """Apply multiple transformations collecting all errors."""
    def apply_transforms(item: T) -> Result[Block[R], str]:
        return (Result.ok(item)
            .bind(lambda x: Result.traverse(
                transformers,
                lambda f: f(x)
            )))
    
    results = items.map(apply_transforms)
    successes = results.choose(lambda r: r.to_option())
    errors = results.choose(lambda r: 
        Option.some(r.error) if r.is_error() else Option.none())
    
    return (Result.ok(successes.collect(lambda x: x))
            if not errors
            else Result.error(errors))

# Usage example
def normalize_email(user: dict) -> Result[dict, str]:
    return (Result.ok(user)
        .map(lambda u: {**u, "email": u["email"].lower()}))

def validate_age(user: dict) -> Result[dict, str]:
    return (Result.ok(user)
        if 0 <= user.get("age", -1) <= 120
        else Result.error(f"Invalid age: {user.get('age')}"))

transformers = Block.of(normalize_email, validate_age)
result = transform_pipeline(users, transformers)
```

### Resource Management
```python
from contextlib import contextmanager
from typing import Iterator, Any

@contextmanager
def manage_resources[T](
    resources: Block[Any],
    setup: Callable[[Any], Result[T, str]],
    cleanup: Callable[[T], None]
) -> Iterator[Result[Block[T], Block[str]]]:
    """Safely manage multiple resources."""
    initialized = Block.empty()
    try:
        results = resources.map(setup)
        successes = results.choose(lambda r: r.to_option())
        errors = results.choose(lambda r: 
            Option.some(r.error) if r.is_error() else Option.none())
        
        yield (Result.ok(successes) if not errors
              else Result.error(errors))
        
        # Cleanup only successful resources
        for resource in successes:
            cleanup(resource)
            
    except Exception as e:
        # Cleanup any successfully initialized resources
        for resource in initialized:
            cleanup(resource)
        raise

# Usage example
def setup_connection(config: dict) -> Result[Connection, str]:
    return Result.ok(create_connection(config))

def cleanup_connection(conn: Connection) -> None:
    conn.close()

configs = Block.of(
    {"host": "localhost", "port": 5432},
    {"host": "remote", "port": 5432}
)

with manage_resources(configs, setup_connection, cleanup_connection) as result:
    # Use connections safely
    result.map(lambda conns: conns.map(process_data))
```

### Batch Processing
```python
def process_in_batches[T, R](
    items: Block[T],
    batch_size: int,
    process: Callable[[Block[T]], Result[Block[R], str]]
) -> Result[Block[R], Block[str]]:
    """Process items in batches collecting all errors."""
    
    # Split into batches
    batches = range(0, len(items), batch_size)
    chunks = Block.of_seq(
        items.skip(i).take(batch_size)
        for i in batches
    )
    
    # Process each batch
    results = chunks.map(process)
    successes = results.choose(lambda r: r.to_option())
    errors = results.choose(lambda r: 
        Option.some(r.error) if r.is_error() else Option.none())
    
    return (Result.ok(successes.collect(lambda x: x))
            if not errors 
            else Result.error(errors))

# Usage example
def process_batch(items: Block[dict]) -> Result[Block[dict], str]:
    return (Result.ok(items)
        .map(lambda xs: xs.map(validate_item))
        .bind(Result.sequence)
        .map(lambda xs: xs.map(transform_item)))

result = process_in_batches(users, 100, process_batch)
```

### Event Processing
```python
@dataclass(frozen=True)
class Event:
    type: str
    data: Any

def event_processor[T](
    events: Block[Event],
    handlers: Map[str, Callable[[Any], Result[T, str]]]
) -> Block[Result[T, str]]:
    """Process events with appropriate handlers."""
    def handle_event(event: Event) -> Result[T, str]:
        return (handlers.try_get(event.type)
            .to_result(f"No handler for {event.type}")
            .bind(lambda h: h(event.data)))
    
    return events.map(handle_event)

# Usage example
def handle_user_created(data: dict) -> Result[User, str]:
    return Result.ok(User(**data))

def handle_user_updated(data: dict) -> Result[User, str]:
    return Result.ok(update_user(**data))

handlers = Map.of_seq([
    ("user_created", handle_user_created),
    ("user_updated", handle_user_updated)
])

events = Block.of(
    Event("user_created", {"name": "Alice"}),
    Event("user_updated", {"id": 1, "name": "Bob"})
)

results = event_processor(events, handlers)

