# Debugging Tools

## Overview
The Expression library provides debugging utilities to help inspect and troubleshoot functional programming patterns, including inspection tools, memoization, and performance monitoring.

## Core Utilities

### Value Inspection
```python
from expression import debug, pipe

def inspect_pipeline(data: Any) -> Any:
    """Inspect values flowing through a pipeline."""
    return pipe(
        data,
        debug(lambda x: print(f"Type: {type(x)}")),
        transform_data,
        debug(lambda x: print(f"Length: {len(x)}")),
        process_data,
        debug(lambda x: print(f"Result: {x}"))
    )
```

### Memoization
```python
from expression import memoize

@memoize
def fibonacci(n: int) -> int:
    """Compute fibonacci with memoization."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Results cached after first call
assert fibonacci(10) == 55  # Computes
assert fibonacci(10) == 55  # Uses cache
```

### Performance Monitoring
```python
def time_execution(f: Callable) -> Any:
    """Monitor function execution time."""
    import time
    
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print(f"{f.__name__} took {end-start:.2f}s")
        return result
    
    return wrapper

@time_execution
@memoize
def slow_function(x: int) -> int:
    time.sleep(1)  # Simulate work
    return x * 2
```

## Common Patterns

### Debug Chain Operations
```python
from expression import Result, Option

def debug_validation_chain(data: dict) -> Result[User, str]:
    """Debug a validation chain."""
    return (Result.ok(data)
        .map(debug(lambda x: print(f"Input: {x}")))
        .bind(validate_required)
        .map(debug(lambda x: print(f"After validation: {x}")))
        .bind(create_user)
        .map(debug(lambda x: print(f"Created user: {x}"))))

def debug_option_chain(key: str) -> Option[str]:
    """Debug an option chain."""
    return (find_value(key)
        .map(debug(lambda x: print(f"Found: {x}")))
        .filter(bool)
        .map(debug(lambda x: print(f"Non-empty: {x}")))
        .map(str.strip)
        .map(debug(lambda x: print(f"Cleaned: {x}"))))
```

### Memory Profiling
```python
from typing import TypeVar, Dict, Callable
from expression import Result, Option
K = TypeVar('K')
V = TypeVar('V')

class DebugMap(Dict[K, V]):
    """Map that tracks access patterns."""
    def __init__(self):
        self.hits: Dict[K, int] = {}
        super().__init__()
    
    def __getitem__(self, key: K) -> Option[V]:
        self.hits[key] = self.hits.get(key, 0) + 1
        return Option.of_obj(super().get(key))

# Usage with memoization
@memoize(cache_class=DebugMap)
def cached_function(x: int) -> Result[int, str]:
    return expensive_computation(x)
```

### Call Tracing
```python
def trace_calls(f: Callable) -> Callable:
    """Trace function calls and their results."""
    def wrapper(*args, **kwargs) -> Result[Any, str]:
        print(f"Calling {f.__name__}({args}, {kwargs})")
        result = f(*args, **kwargs)
        print(f"{f.__name__} returned {result}")
        return Result.ok(result)
    return wrapper

@trace_calls
def process_data(x: int) -> Result[int, str]:
    return Result.ok(x * 2)
```

## Best Practices

### DO ✓
- Use debug() for temporary inspection
- Profile performance bottlenecks
- Monitor memory usage patterns
- Cache expensive computations
- Clear memoization caches
- Document debugging tools
- Use type-safe debugging

### DON'T ✗
- Leave debug calls in production
- Ignore memory leaks
- Cache volatile data
- Mix debug/production code
- Create debugging side effects
- Forget to cleanup resources
- Debug with print statements

## Integration Examples

### With Collections
```python
from expression.collections import Block, Seq

def debug_collection_pipeline(items: Block[str]) -> Result[Block[int], str]:
    """Debug collection transformations."""
    return (Result.ok(items)
        .map(debug(lambda xs: print(f"Processing items: {len(xs)}")))
        .map(lambda xs: xs.filter(bool))
        .map(debug(lambda xs: print(f"Non-empty items: {len(xs)}")))
        .map(lambda xs: xs.map(safe_parse_int))
        .map(debug(lambda xs: print(f"Parsed numbers: {len(xs)}"))))

def safe_parse_int(s: str) -> Result[int, str]:
    return (Result.ok(s)
        .map(str.strip)
        .filter(bool)
        .bind(lambda x: 
            Result.ok(int(x))
            .map_error(lambda _: f"Invalid integer: {x}")))

def debug_lazy_evaluation(items: Seq[str]) -> None:
    """Debug lazy sequence processing."""
    transformed = (items
        .map(debug(lambda x: print(f"Mapping: {x}")))
        .filter(debug(lambda x: print(f"Filtering: {x}")))
        .take(2))
    
    print("Transformation defined but not executed")
    list(transformed)  # Now executes and prints debug info
```

### With Error Handling
```python
def debug_error_chain(data: Any) -> Result[Any, str]:
    """Debug error handling chain."""
    return (Result.ok(data)
        .map(debug(lambda x: print(f"Input: {x}")))
        .bind(validate_input)
        .map(debug(lambda x: print(f"Validated: {x}")))
        .bind(transform_data)
        .map(debug(lambda x: print(f"Transformed: {x}")))
        .map_error(debug(lambda e: print(f"Error: {e}"))))
```

## Performance Considerations

### Cache Management
```python
from functools import lru_cache

# Memory-sensitive caching
@lru_cache(maxsize=100)
def limited_cache(x: int) -> int:
    return expensive_computation(x)

def clear_caches() -> None:
    """Clear all memoization caches."""
    fibonacci.cache_clear()
    limited_cache.cache_clear()
```

### Debug Mode Control
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DebugConfig:
    enabled: bool = False
    log_file: Optional[str] = None
    trace_calls: bool = False

debug_config = DebugConfig()

def debug_wrapper(f: Callable) -> Callable:
    """Conditional debugging wrapper."""
    def wrapper(*args, **kwargs) -> Result[Any, str]:
        if debug_config.enabled:
            print(f"Debug: calling {f.__name__}")
        return Result.ok(f(*args, **kwargs))
    return wrapper
```

## Testing Examples

### Debug Tool Tests
```python
def test_debug_inspection():
    calls = []
    
    # Create debug probe
    probe = debug(lambda x: calls.append(x))
    
    # Use in pipeline
    result = (Result.ok("test")
        .map(str.upper)
        .map(probe)
        .map(str.lower))
    
    assert result.value == "test"
    assert calls == ["TEST"]

def test_memoization():
    calls = 0
    
    @memoize
    def tracked_function(x: int) -> int:
        nonlocal calls
        calls += 1
        return x * 2
    
    # First call computes
    assert tracked_function(1) == 2
    assert calls == 1
    
    # Second call uses cache
    assert tracked_function(1) == 2
    assert calls == 1
```

### Performance Tests
```python
def test_performance_monitoring():
    @time_execution
    def slow_operation() -> None:
        time.sleep(0.1)
    
    start = time.time()
    slow_operation()
    duration = time.time() - start
    
    assert 0.1 <= duration <= 0.2