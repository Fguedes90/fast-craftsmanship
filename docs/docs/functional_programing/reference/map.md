# Map

## Overview
An immutable dictionary implementation optimized for functional programming patterns. While Block handles sequences and Seq handles lazy evaluation, Map specializes in key-value associations with guaranteed immutability and type safety.

## Choosing the Right Collection
| Feature Needed | Use |
|----------------|-----|
| Sequential data | Block |
| Lazy evaluation | Seq |
| Key-value pairs | Map |
| Large datasets | Seq |
| Fast lookups | Map |
| Thread safety | Any (all are immutable) |

## When to Use
✓ Need key-value associations
✓ Frequent lookups by key
✓ Type-safe dictionary operations
✓ Need immutable mappings
✓ Complex key-based transformations

## When Not to Use
✗ Sequential data (use Block instead)
✗ Large datasets needing lazy eval (use Seq)
✗ Simple list operations (use Block)
✗ Need ordered sequences (use Block)
✗ Memory is critically constrained

## Core Operations

### Creation
```python
from expression.collections import Map

# From key-value pairs
scores = Map.of_seq([("Alice", 90), ("Bob", 85)])

# Empty map
empty = Map.empty()

# Add entries
new_scores = scores.add("Charlie", 95)
```

### Essential Operations
| Operation | Description | Returns | Example |
|-----------|-------------|---------|---------|
| `add(k, v)` | Add/update entry | `Map[K, V]` | `m.add("key", 1)` |
| `remove(k)` | Remove entry | `Map[K, V]` | `m.remove("key")` |
| `try_get(k)` | Safe lookup | `Option[V]` | `m.try_get("key")` |
| `keys()` | Get all keys | `Block[K]` | `m.keys()` |
| `values()` | Get all values | `Block[V]` | `m.values()` |

### Transformations
```python
# Filter entries
high_scores = scores.filter(lambda _, score: score >= 90)

# Transform values
percentages = scores.map(lambda _, score: f"{score}%")

# Transform with keys
labels = scores.map(lambda name, score: f"{name}: {score}")
```

## Common Patterns

### Safe Data Access
```python
def get_score(name: str) -> str:
    return scores.try_get(name).match(
        lambda score: f"Score: {score}",
        lambda: "Not found"
    )

assert get_score("Alice") == "Score: 90"
assert get_score("Unknown") == "Not found"
```

### Data Processing
```python
def process_scores() -> Map[str, float]:
    return (scores
        .filter(lambda _, score: score > 0)     # Remove invalid
        .map(lambda name, score: score / 100))  # Convert to decimal
```

### Batch Operations
```python
def update_scores(updates: Map[str, int]) -> Map[str, int]:
    """Update scores while preserving originals."""
    return scores.union(updates)
```

## Best Practices

### DO ✓
- Use `try_get` for safe access
- Chain transformations
- Handle missing keys explicitly
- Keep maps immutable
- Use type hints

### DON'T ✗
- Mutate maps (not possible, but good to know)
- Mix with mutable dicts
- Ignore missing key cases
- Create unnecessary intermediates
- Use for simple key-value storage

## Integration

### With Option
```python
def safe_increment(scores: Map[str, int], name: str) -> Option[int]:
    return scores.try_get(name).map(lambda x: x + 1)
```

### With Result
```python
def validate_score(scores: Map[str, int], name: str) -> Result[int, str]:
    return (scores.try_get(name)
        .to_result(f"No score for {name}")
        .bind(lambda score: 
            Result.ok(score) if score >= 0
            else Result.error("Invalid score")))
```

## Integration with Other Collections

### With Block
```python
def index_by_key[K, V](items: Block[V], key_fn: Callable[[V], K]) -> Map[K, V]:
    """Create a map from a block using a key function."""
    return Map.of_seq((key_fn(x), x) for x in items)

def to_block(map: Map[K, V]) -> Block[tuple[K, V]]:
    """Convert map entries to a block of pairs."""
    return Block.of_seq(map.items())
```

### With Seq
```python
def process_large_dataset(data: Seq[dict]) -> Map[str, int]:
    """Process large dataset lazily and create final map."""
    return Map.of_seq(
        (item['key'], process(item))
        for item in data
        if is_valid(item)
    )
```

## Performance Characteristics
| Operation | Complexity | Note |
|-----------|------------|------|
| Lookup | O(log n) | Red-black tree |
| Insert | O(log n) | Maintains balance |
| Remove | O(log n) | Preserves structure |
| Union | O(n log n) | Merges trees |

## Advanced Features

### Type Parameters 
- `K`: Key type (must be comparable)
- `V`: Value type
- `R`: Result type for transformations

### Module Functions
```python
# Create from sequence
Map.of_seq(pairs)  # → Map[K, V]

# Merge maps
Map.union(maps)    # → Map[K, V]

# Empty map
Map.empty()        # → Map[K, V]
```

## Testing Examples

### Unit Testing
```python
def test_map_operations():
    scores = Map.of_seq([("A", 90), ("B", 85)])
    
    # Test immutability
    new_scores = scores.add("C", 95)
    assert "C" not in scores
    assert new_scores.try_get("C").value == 95
    
    # Test transformations
    high_scores = scores.filter(lambda _, s: s >= 90)
    assert len(high_scores) == 1
    assert "A" in high_scores
```

### Property Testing
```python
from hypothesis import given
from hypothesis import strategies as st

@given(st.dictionaries(st.text(), st.integers()))
def test_map_properties(data: dict):
    # Convert to Map
    m = Map.of_seq(data.items())
    
    # Properties
    assert len(m) == len(data)
    for k, v in data.items():
        assert m.try_get(k).value == v
```

## Common Use Cases

### Configuration Management
```python
def load_config(data: dict) -> Result[Map[str, Any], str]:
    """Load and validate configuration."""
    return (Result.ok(Map.of_seq(data.items()))
        .map(lambda m: m.map(
            lambda k, v: validate_value(k, v)))
        .bind(Result.sequence))
```

### Data Transformation
```python
def normalize_data(data: Map[str, float]) -> Map[str, float]:
    """Normalize values to [0,1] range."""
    max_val = data.values().max_or(1)
    return data.map(lambda _, v: v / max_val)
```

### Caching
```python
class Cache:
    def __init__(self):
        self._data = Map.empty()
        
    def get(self, key: str) -> Option[Any]:
        return self._data.try_get(key)
        
    def set(self, key: str, value: Any) -> 'Cache':
        self._data = self._data.add(key, value)
        return self
```

### Safe Resource Access
```python
class ResourceCache:
    def __init__(self):
        self._data = Map.empty()
        
    def get(self, key: str) -> Option[Any]:
        return self._data.try_get(key)
        
    def with_resource[T](self, key: str, f: Callable[[Any], Result[T, str]]) -> Result[T, str]:
        return (self._data.try_get(key)
            .to_result(f"Resource {key} not found")
            .bind(f))