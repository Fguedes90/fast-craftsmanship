# Railway Oriented Programming (ROP)

Railway Oriented Programming (ROP) is a functional error handling technique that uses types to model errors instead of exceptions. This approach can lead to more robust and easier-to-maintain code. The `expression` library provides a `Result` type that facilitates ROP in Python.

## Result in Expression

The `Result[T, TError]` type in `expression` allows you to write composable, error-tolerant code. A `Result` is similar to `Option`, but it lets you define the type of error, such as an exception. This is useful when you need to know why an operation failed.  It serves the same purpose as an `Either` type, where `Left` represents the error and `Right` the success value.

```python
from expression import Ok, Error

def fetch(url):
    try:
        if not "http://" in url:
            raise Exception("Error: unable to fetch from: '%s'" % url)

        value = url.replace("http://", "")
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```python
result = fetch("http://42")
print(result)
```

```python
def parse(string):
    try:
        value = float(string)
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```python
result = parse("42")
print(result)
```

## Composition with Pipeline

The `expression` library provides a `pipeline` function for composing functions that return `Result` types. This is also known as "Kleisli composition."

```python
from expression.extra.result import pipeline

def fetch_with_value(x):
    return fetch("http://%s" % x)

request = pipeline(
    fetch,
    fetch_with_value,
    fetch_with_value,
    parse
)

result = request("http://123")
print(result)
```

## Effect notation

```python
from expression import effect, Ok, Result

@effect.result[int, Exception]()
def fn():
    x = yield from Ok(42)
    y = yield from Ok(10)
    return x + y

xs = fn()
assert isinstance(xs, Result)
```

A simplified type called [`Try`](reference_try) is also available. It's a result type
that is pinned to `Exception` i.e., `Result[TSource, Exception]`. This makes the code
simpler since you don't have specify the error type every time you declare the type of
your result.
