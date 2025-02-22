# Concurrency

## Overview
The Expression library provides tools for safe concurrent programming through message passing and actor-like patterns. These tools enable building thread-safe applications without direct sharing of mutable state.

## Core Concepts

### Mailbox
Thread-safe message queues for communication between threads:
```python
from expression import mailbox

# Create mailbox
mb = mailbox()

# Bounded mailbox
mb_bounded = mailbox(max_size=100)

# Basic operations
mb.post("message")       # Send message
msg = mb.receive()       # Blocking receive
opt = mb.try_receive()   # Non-blocking receive
found = mb.scan(pred)    # Find matching message
```

### Thread Safety
All Expression data structures are immutable and thread-safe:
```python
from expression.collections import Block
from concurrent.futures import ThreadPoolExecutor

def parallel_process(items: Block[T]) -> Block[R]:
    """Safe parallel processing with immutable collections."""
    with ThreadPoolExecutor() as pool:
        return Block.of_seq(pool.map(process, items))
```

## Common Patterns

### Worker Pool
```python
def worker(tasks: Mailbox[Task], results: Mailbox[Result]):
    while True:
        task = tasks.receive()
        if task.is_stop():
            break
        result = process_task(task)
        results.post(result)

def create_worker_pool(size: int) -> tuple[Mailbox, Mailbox]:
    tasks = mailbox()
    results = mailbox()
    workers = [Thread(target=worker, args=(tasks, results)) 
              for _ in range(size)]
    for w in workers:
        w.start()
    return tasks, results
```

### Event Processing
```python
@dataclass
class Event:
    type: str
    data: Any

class EventBus:
    def __init__(self):
        self.subscribers = []
        
    def subscribe(self, mb: Mailbox[Event]):
        self.subscribers.append(mb)
        
    def publish(self, event: Event):
        for subscriber in self.subscribers:
            subscriber.post(event)

def event_processor(events: Mailbox[Event], 
                   handlers: dict[str, Callable]):
    while True:
        event = events.receive()
        if event.type in handlers:
            handlers[event.type](event.data)
```

### Resource Pool
```python
from typing import TypeVar, Callable
from expression import Result, Option
from contextlib import contextmanager

T = TypeVar('T')
R = TypeVar('R')

class ResourcePool:
    def __init__(self, size: int):
        self.resources = mailbox()
        for _ in range(size):
            self.create_resource()
    
    def create_resource(self) -> None:
        resource = (Result.ok(None)
            .bind(lambda _: initialize_resource())
            .match(
                lambda r: self.resources.post(r),
                lambda e: print(f"Failed to create resource: {e}")
            ))
            
    def with_resource[T](self, f: Callable[[Resource], Result[T, str]]) -> Result[T, str]:
        resource = self.resources.receive()
        
        def release() -> None:
            self.resources.post(resource)
        
        return (Result.ok(resource)
            .bind(f)
            .ensure(release))
```

## Integration Patterns

### With Option/Result
```python
def safe_receive(mb: Mailbox[T]) -> Option[T]:
    """Non-blocking message receive."""
    return mb.try_receive()

def validated_send(mb: Mailbox[T], msg: T) -> Result[None, str]:
    """Validated message send."""
    try:
        mb.post(msg)
        return Result.ok(None)
    except Exception as e:
        return Result.error(str(e))
```

### With Collections
```python
def batch_process(mb: Mailbox[T], 
                 batch_size: int) -> Block[R]:
    """Process messages in batches."""
    messages = Block.empty()
    for _ in range(batch_size):
        mb.try_receive().match(
            lambda msg: messages.cons(msg),
            lambda: None
        )
    return messages.map(process_message)
```

## Best Practices

### DO ✓
- Use typed messages
- Handle stopping conditions
- Implement timeouts
- Monitor queue sizes
- Document message protocols
- Use bounded queues
- Handle backpressure
- Test concurrent scenarios

### DON'T ✗
- Share mutable state
- Block indefinitely
- Mix with locks/mutexes
- Ignore queue capacity
- Pass complex objects
- Create deep dependencies
- Ignore error handling
- Leave resources unclosed

## Performance Considerations

1. Message Passing
   - Use appropriate queue sizes
   - Consider message batching
   - Monitor queue depths
   - Handle backpressure
   - Profile message patterns

2. Resource Usage
   - Pool expensive resources
   - Implement timeouts
   - Clean up properly
   - Monitor thread usage
   - Handle overload scenarios

## Testing

### Unit Tests
```python
def test_mailbox_operations():
    mb = mailbox()
    
    # Test post/receive
    mb.post("test")
    assert mb.receive() == "test"
    
    # Test try_receive
    assert mb.try_receive().is_none()
    
    # Test scanning
    mb.post(1)
    mb.post(2)
    assert mb.scan(lambda x: x > 1).value == 2
```

### Concurrency Tests
```python
def test_concurrent_access():
    mb = mailbox()
    count = 100
    
    def sender():
        for i in range(count):
            mb.post(i)
            
    def receiver(results: list):
        for _ in range(count):
            results.append(mb.receive())
            
    # Run concurrent threads
    results = []
    s = Thread(target=sender)
    r = Thread(target=receiver, args=(results,))
    s.start(); r.start()
    s.join(); r.join()
    
    assert len(results) == count
    assert sorted(results) == list(range(count))
```

### Integration Tests
```python
def test_worker_pool():
    tasks, results = create_worker_pool(2)
    
    # Send tasks
    for i in range(5):
        tasks.post(Task(i))
        
    # Verify results
    processed = [results.receive() for _ in range(5)]
    assert len(processed) == 5
```

## Real World Examples

### Task Queue System
```python
class TaskQueue:
    def __init__(self, num_workers: int):
        self.tasks = mailbox()
        self.results = mailbox()
        self.workers = [
            Thread(target=self._worker)
            for _ in range(num_workers)
        ]
        for w in self.workers:
            w.start()
    
    def _worker(self):
        while True:
            task = self.tasks.receive()
            if task.is_stop():
                break
            
            result = (Result.ok(task)
                .bind(lambda t: Result.ok(t.execute()))
                .map_error(lambda e: str(e)))
            
            self.results.post(result)
    
    def submit(self, task: Task) -> None:
        self.tasks.post(task)
    
    def get_result(self) -> Result[Any, str]:
        return self.results.receive()
```

### Event Processing System
```python
class EventProcessor:
    def __init__(self):
        self.events = mailbox()
        self.processors: dict[str, list[Mailbox]] = {}
    
    def subscribe(self, event_type: str, handler: Mailbox):
        if event_type not in self.processors:
            self.processors[event_type] = []
        self.processors[event_type].append(handler)
    
    def publish(self, event: Event):
        self.events.post(event)
    
    def run(self):
        while True:
            event = self.events.receive()
            handlers = self.processors.get(event.type, [])
            for handler in handlers:
                handler.post(event)
```

### Message Processing
```python
def process_messages(input_mb: Mailbox[bytes]) -> Result[Seq[str], str]:
    def decode_message(data: bytes) -> Result[str, str]:
        return (Result.ok(data)
            .bind(safe_decode)
            .filter(is_valid_message)
            .bind(parse_message))
    
    return (Result.ok(seq(iter(input_mb.receive, None)))
        .map(lambda xs: xs
            .map(decode_message)
            .filter(lambda r: r.is_ok())
            .map(lambda r: r.value)))
```

### Event Broadcasting
```python
from dataclasses import dataclass
from typing import Any, List

@dataclass
class Event:
    type: str
    data: Any

class EventBus:
    def __init__(self):
        self.subscribers: List[Mailbox[Result[Event, str]]] = []
        
    def subscribe(self, mb: Mailbox[Result[Event, str]]) -> None:
        self.subscribers.append(mb)
        
    def publish(self, event: Event) -> None:
        result = (Result.ok(event)
            .bind(validate_event)
            .map_error(lambda e: f"Invalid event: {e}"))
            
        for subscriber in self.subscribers:
            subscriber.post(result)