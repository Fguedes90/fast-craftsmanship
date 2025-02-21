# Containers in Python with Expression Library

## Core Concepts

Containers in Python are objects that can hold other objects. The Expression library enhances Python's container capabilities with immutable implementations.

## Immutable Collections

### Block (Immutable List)

```python
from expression.collections import Block

# DO ✅
def process_numbers():
    numbers = Block.of_seq(range(3))  # [0, 1, 2]
    return numbers.cons(3)            # [3, 0, 1, 2]

# DON'T ❌
def mutate_list():
    numbers = [0, 1, 2]
    numbers.append(3)  # Mutates original list
    return numbers

# WHY: Block ensures immutability and thread-safety while maintaining readability
```

### Map (Immutable Dictionary)

```python
from expression.collections import Map

# DO ✅
def filter_scores():
    scores = Map.of_seq([("Alice", 90), ("Bob", 70)])
    is_high_score = lambda _, v: v >= 80
    return scores.filter(is_high_score)

# DON'T ❌
def mutate_dict():
    scores = {"Alice": 90, "Bob": 70}
    scores.pop("Bob")  # Mutates original dict
    return scores

# WHY: Map provides immutable operations and functional-style transformations
```

## Key Benefits

1. Thread Safety
2. Predictable State
3. Easy Testing
4. Functional Programming Friendly

## Best Practices

### DO ✅
- Use Block instead of List for immutable sequences
- Use Map instead of Dict when immutability is needed
- Chain operations using functional methods
- Write pure functions that return new containers

### DON'T ❌
- Modify container contents after creation
- Mix mutable and immutable data structures
- Use global state
- Perform side effects inside container operations

## Practical Example

```python
from expression.collections import Block, Map

# DO ✅
def process_user_data(users: Block[str], scores: Map[str, int]):
    is_high_scorer = lambda _, score: score > 80
    has_high_score = lambda user: user in high_scorers
    
    high_scorers = scores.filter(is_high_scorer)
    return users.filter(has_high_score)

# DON'T ❌
def process_user_data_mutable(users: list, scores: dict):
    for user in users[:]:  # Creates copy to avoid modification during iteration
        if scores.get(user, 0) <= 80:
            users.remove(user)
    return users

# WHY: The immutable approach is more predictable, testable, and thread-safe
```

## Testing Example

```python
def test_process_user_data():
    users = Block.of_seq(["Alice", "Bob", "Charlie"])
    scores = Map.of_seq([("Alice", 90), ("Bob", 70), ("Charlie", 85)])
    
    result = process_user_data(users, scores)
    
    assert len(result) == 2
    assert "Alice" in result
    assert "Charlie" in result
    assert "Bob" not in result
