# Callbacks and Continuations

> Don't call me. I'll call you.

```python
import threading

def long_running(callback):
    def done():
        result = 42
        callback(result)
    timer = threading.Timer(5.0, done)
    timer.start()

long_running(print)
```

## Continuation Passing Style (CPS)

This is a functional programming style where you don’t return any values from your
functions. Instead of returning the result, you pass a continuation function that will
be applied to the result.

```python
import math
from expression import Cont

def add(a, b):
    return Cont.Return(a + b)

def square(x):
    return Cont.Return(x * x)

def sqrt(x):
    return Cont.Return(math.sqrt(x))

def pythagoras(a, b):
    return square(a).bind(lambda aa:
           square(b).bind(lambda bb:
           add(aa, bb).bind(lambda aabb:
           sqrt(aabb))))
```

```python
result = pythagoras(2, 3).run()
print(result)
```

## Conclusion

Continuation Passing Style (CPS) can be effectively managed using the `expression` library in Python, leading to cleaner and more maintainable code.
