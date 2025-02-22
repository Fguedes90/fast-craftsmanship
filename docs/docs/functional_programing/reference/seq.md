# Seq

## Contents
1. [Overview](#overview)
2. [Collection Type Comparison](#collection-type-comparison)
3. [API Reference](#api-reference)
   - [Creation Methods](#creation-methods)
   - [Transform Methods](#transform-methods)
   - [Operation Methods](#operation-methods)
4. [Common Patterns](#common-patterns)
5. [Integration Patterns](#integration-patterns)
6. [Performance Notes](#performance-notes)
7. [Best Practices](#best-practices)
8. [Testing Patterns](#testing-patterns)
9. [Recipes](#recipes)

## Overview
Seq provides lazy sequence operations for efficient processing of large or infinite data sets through deferred evaluation. While Block is ideal for small to medium collections and Map for key-value pairs, Seq specializes in memory-efficient processing of large datasets.

## Collection Type Comparison
| Feature | Seq | Block | Map |
|---------|-----|-------|-----|
| Evaluation | Lazy | Eager | Eager |
| Memory Usage | O(1)* | O(n) | O(n) |
| Best For | Large/Infinite | Small/Medium | Key-Value |
| Access Pattern | Sequential | Random | Key-based |
| Thread Safety | Yes | Yes | Yes |
*For transformer operations

## When to Use
✓ Processing very large datasets
✓ Working with infinite sequences
✓ Memory constraints present
✓ Streaming data processing
✓ Complex data pipelines needing lazy eval

## When Not to Use
✗ Small collections (use Block)
✗ Need key-value pairs (use Map)
✗ Random access needed (use Block)
✗ Need eager evaluation (use Block)
✗ Need indexed access (use Block)

## API Reference

### Creation Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `seq(xs)` | From iterable | `seq(range(10))` | [Common Patterns](#lazy-evaluation) |
| `empty()` | Empty sequence | `Seq.empty()` | [Integration Patterns](#with-collections) |
| `unfold(s,f)` | Generate sequence | `Seq.unfold(0, next)` | [Recipes](#infinite-sequences) |
| `iterate(x,f)` | Repeated application | `Seq.iterate(1, double)` | [Common Patterns](#lazy-evaluation) |

### Transform Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `map(f)` | Transform items | `xs.map(str)` | [Performance Notes](#memory-usage) |
| `filter(p)` | Keep matching | `xs.filter(bool)` | [Best Practices](#lazy-chains) |
| `flat_map(f)` | Map and flatten | `xs.flat_map(expand)` | [Integration Patterns](#with-collections) |
| `scan(f,s)` | Running accumulation | `xs.scan(add, 0)` | [Recipes](#stateful-processing) |

### Operation Methods
| Method | Description | Example | See Also |
|--------|-------------|---------|----------|
| `take(n)` | First n items | `xs.take(5)` | [Performance Notes](#evaluation-control) |
| `skip(n)` | Drop n items | `xs.skip(5)` | [Common Patterns](#streaming) |
| `fold(f,s)` | Accumulate all | `xs.fold(add, 0)` | [Best Practices](#eager-operations) |
| `reduce(f)` | Combine items | `xs.reduce(max)` | [Common Patterns](#aggregation) |

## Common Patterns

### Lazy Evaluation
```python
def process_large_file(path: str) -> Seq[dict]:
    """Process large file lazily."""
    return (seq(open(path))         # Read lines lazily
        .map(str.strip)             # Clean lines
        .filter(bool)               # Remove empty
        .map(parse_json)           # Parse each line
        .filter(is_valid))         # Keep valid only

# Nothing computed until iteration
results = process_large_file("large.jsonl")
# Process one item at a time
for item in results:
    process_item(item)
```

### Streaming
```python
def stream_process[T](source: Iterable[T]) -> Seq[R]:
    """Stream processing with constant memory."""
    return (seq(source)
        .map(transform)          # Transform items
        .filter(is_valid)        # Filter invalid
        .map(process)           # Process each
        .take(100))            # Limit results
```

### Infinite Sequences
```python
def fibonacci() -> Seq[int]:
    """Generate infinite Fibonacci sequence."""
    def next_fib(state: tuple[int, int]) -> tuple[int, tuple[int, int]]:
        curr, next = state
        return curr, (next, curr + next)
    
    return Seq.unfold((0, 1), next_fib)

# Take first 10 Fibonacci numbers
fibs = fibonacci().take(10)
assert list(fibs) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### Aggregation
```python
def analyze_data(data: Seq[float]) -> dict[str, float]:
    """Compute statistics in single pass."""
    def combine(acc: dict, x: float) -> dict:
        count, sum_, min_, max_ = acc.values()
        return {
            "count": count + 1,
            "sum": sum_ + x,
            "min": min(min_, x),
            "max": max(max_, x)
        }
    
    initial = {"count": 0, "sum": 0, "min": float('inf'), "max": float('-inf')}
    return data.fold(combine, initial)
```

## Integration Patterns

### With Collections
```python
def to_block(xs: Seq[T]) -> Block[T]:
    """Convert to Block when size is manageable."""
    return Block.of_seq(xs)

def to_map(xs: Seq[tuple[K, V]]) -> Map[K, V]:
    """Convert key-value pairs to Map."""
    return Map.of_seq(xs)

def block_to_seq(xs: Block[T]) -> Seq[T]:
    """Convert Block to lazy Seq."""
    return seq(xs)
```

### With Option/Result
```python
def safe_process(xs: Seq[T]) -> Seq[Result[R, str]]:
    """Process items safely."""
    return (xs
        .map(validate)         # Returns Option[T]
        .filter(Option.is_some)
        .map(lambda o: o
            .to_result("Invalid")
            .bind(transform)))

def collect_results(xs: Seq[Result[T, str]]) -> Result[Seq[T], list[str]]:
    """Collect successful results."""
    def combine(acc: Result[list[T], list[str]], 
               x: Result[T, str]) -> Result[list[T], list[str]]:
        return acc.bind(lambda items:
            x.map(lambda item: [*items, item])
             .map_error(lambda e: [e]))
    
    return (xs.fold(combine, Result.ok([]))
            .map(lambda items: seq(items)))
```

### Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor

def parallel_process[T, R](
    xs: Seq[T], 
    f: Callable[[T], R],
    chunk_size: int = 1000,
    max_workers: int = 4
) -> Seq[R]:
    """Process sequence in parallel chunks."""
    def process_chunk(chunk: list[T]) -> list[R]:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            return list(executor.map(f, chunk))
    
    return (xs
        .chunk(chunk_size)      # Split into chunks
        .map(process_chunk)     # Process each chunk
        .flat_map(seq))        # Flatten results
```

## Performance Notes

### Memory Usage
- Constant memory for transformers
- No intermediate collections
- Chunk processing for parallelism
- Careful with materialization

### Evaluation Control
- Lazy until terminal operation
- Process only what's needed
- Chain operations efficiently
- Control batch sizes

## Best Practices

### DO ✓
- Use for large datasets
- Chain operations lazily
- Control evaluation points
- Process in chunks
- Handle infinite sequences

### DON'T ✗
- Materialize unnecessarily
- Create deep call chains
- Mix lazy/eager operations
- Hold references to iterators
- Ignore memory constraints

## Testing Patterns

### Unit Tests
```python
def test_seq_operations():
    """Test basic sequence operations."""
    numbers = seq(range(10))
    
    # Test lazy evaluation
    transformed = numbers.map(lambda x: x * 2)
    assert not isinstance(transformed, list)
    
    # Test materialization
    result = list(transformed)
    assert result == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### Property Tests
```python
@given(st.lists(st.integers()))
def test_seq_properties(xs: list[int]):
    """Test sequence properties."""
    sequence = seq(xs)
    
    # Map preserves length
    mapped = sequence.map(str)
    assert len(list(mapped)) == len(xs)
    
    # Filter creates subsequence
    filtered = sequence.filter(lambda x: x > 0)
    assert all(x > 0 for x in filtered)
```

## Recipes

### Stateful Processing
```python
def running_average(xs: Seq[float]) -> Seq[float]:
    """Compute running average of sequence."""
    def update(state: tuple[int, float], x: float) -> tuple[float, tuple[int, int]]:
        count, total = state
        new_count = count + 1
        new_total = total + x
        return new_total / new_count, (new_count, new_total)
    
    return Seq.unfold((0, 0.0), lambda s: 
        update(s, next(xs.__iter__())))

def window_stats(xs: Seq[T], size: int) -> Seq[dict]:
    """Compute moving window statistics."""
    return (xs
        .window(size)                    # Create windows
        .map(lambda w: seq(w).fold(     # Process each window
            lambda acc, x: {
                "min": min(acc["min"], x),
                "max": max(acc["max"], x),
                "sum": acc["sum"] + x,
                "count": acc["count"] + 1
            },
            {"min": float('inf'), "max": float('-inf'),
             "sum": 0, "count": 0}
        )))
```

### Custom Iteration
```python
def bounded_retry[T](
    operation: Callable[[], Result[T, str]],
    max_attempts: int = 3,
    delay: float = 1.0
) -> Seq[Result[T, str]]:
    """Generate sequence of retry attempts."""
    def attempt(state: tuple[int, float]) -> Option[tuple[Result[T, str], tuple[int, float]]]:
        attempt_num, wait = state
        if attempt_num >= max_attempts:
            return Nothing
            
        time.sleep(wait)
        result = operation()
        if result.is_ok():
            return Nothing
            
        return Some((result, (attempt_num + 1, wait * 2)))
    
    return Seq.unfold((0, delay), attempt)

# Usage example
def api_call() -> Result[dict, str]:
    return Result.error("Network error")

retries = bounded_retry(api_call)
for result in retries:
    print(f"Attempt failed: {result.error}")