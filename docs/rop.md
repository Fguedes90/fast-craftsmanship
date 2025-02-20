---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
(tutorial_railway)=

# Railway Oriented Programming (ROP)

- We don't really want to raise exceptions since it makes the code bloated with error
  checking
- It's easy to forget to handle exceptions, or handle the wrong type of exception
- Dependencies might even change the kind of exceptions they throw
- Let's model errors using types instead

```{code-cell} python
class Result:
    pass

class Ok(Result):
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "Ok %s" % str(self._value)

class Error(Result):
    def __init__(self, exn):
        self._exn = exn

    def __str__(self):
        return "Error %s" % str(self._exn)
```

The Expression library contains a similar but more feature complete Result class we can
use:

```{code-cell} python
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

```{code-cell} python
result = fetch("http://42")

print(result)
```

```{code-cell} python
def parse(string):
    try:
        value = float(string)
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```{code-cell} python
result = parse("42")

print(result)
```

## Composition

How should we compose Result returning functions? How can we make a `fetch_parse` from
`fetch` and `parse`.

We cannot use functional composition here since signatures don't match.

```python
def compose(fn: Callable[[A], Result[B, TError]], gn: Callable[[B], Result[C, TError]]) -> Callable[[A], Result[C, TError]]:
    lambda x: ...
```

First we can try to solve this with an "imperative" implementation using type-checks and
`if-else` statements:

```{code-cell} python
def fetch_parse(url):
    b = fetch(url)
    if isinstance(b, Ok):
        val_b = b._value # <--- Don't look inside the box!!!
        return parse(val_b)
    else: # Must be error
        return b

result = fetch_parse("http://42")
print(result)
```

This works, but the code is not easy to read. We have also hard-coded the logic to it's
not possible to easily reuse without copy/paste. Here is a nice example on how to solve
this by mixing object-oriented code with functional thinking:

```{code-cell} python
class Ok(Result):
    def __init__(self, value):
        self._value = value

    def bind(self, fn):
        return fn(self._value)

    def __str__(self):
        return "Ok %s" % str(self._value)

class Error(Result):
    def __init__(self, exn):
        self._exn = exn

    def bind(self, fn):
        return self

    def __str__(self):
        return "Error %s" % str(self._exn)

def bind(fn, result):
    """We don't want method chaining in Python."""
    return result.bind(fn)
```

```{code-cell} python
result = bind(parse, fetch("http://42"))
print(result)
```

```{code-cell} python
def compose(f, g):
    return lambda x: f(x).bind(g)

fetch_parse = compose(fetch, parse)
result = fetch_parse("http://123.0")
print(result)
```

```{code-cell} python
result = fetch("http://invalid").bind(parse)
print(result)
```

### But what if we wanted to call fetch 10 times in a row?

This is what's called the "Pyramide of Doom":

```{code-cell} python
from expression.core import result

result = bind(parse,
            bind(lambda x: fetch("http://%s" % x),
               bind(lambda x: fetch("http://%s" % x),
                  bind(lambda x: fetch("http://%s" % x),
                     bind(lambda x: fetch("http://%s" % x),
                         bind(lambda x: fetch("http://%s" % x),
                             bind(lambda x: fetch("http://%s" % x),
                                 fetch("http://123")
                            )
                         )
                     )
                  )
               )
            )
         )
print(result)
```

## Can we make a more generic compose?

Let's try to make a general compose function that composes two result returning functions:

```{code-cell} python
def compose(f, g):
    return lambda x: f(x).bind(g)

fetch_parse = compose(fetch, parse)
result = fetch_parse("http://42")
print(result)
```

## Pipelining

Functional compose of functions that returns wrapped values is called pipeling in the
Expression library. Other languages calls this "Kleisli composition". Using a reducer we
can compose any number of functions:

```{code-cell} python
from functools import reduce

def pipeline(*fns):
    return reduce(lambda res, fn: lambda x: res(x).bind(fn), fns)
```

Now, make `fetch_and_parse` using kleisli:

```{code-cell} python
fetch_and_parse = pipeline(fetch, parse)
result = fetch_and_parse("http://123")
print(result)
```

### What if we wanted to call fetch 10 times in a row?

```{code-cell} python
from expression.extra.result import pipeline

fetch_with_value = lambda x: fetch("http://%s" % x)

request = pipeline(
            fetch,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            fetch_with_value,
            parse
          )

result = request("http://123")
print(result)
```

## Result in Expression

The `Result[T, TError]` type in Expression lets you write error-tolerant code that can
be composed. A Result works similar to `Option`, but lets you define the value used for
errors, e.g., an exception type or similar. This is great when you want to know why some
operation failed (not just `Nothing`). This type serves the same purpose of an `Either`
type where `Left` is used for the error condition and `Right` for a success value.

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

---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---
(tutorial_optional_values)=

# Optional Values

Sometimes we don't have a value for a given variable. Perhaps the value is not known or
available yet. In Python we represent the absence of a value with the special value
`None`. In other languages there is usually a `null` value.

```{code-cell} python
xs = None
print(xs)
```

Without type hints we don't really know if the value is supposed to be `None´ or
something else.


## Null Reference Exceptions

> The billion-dollar mistake

Speaking at a software conference in 2009, Tony Hoare apologized for inventing the null
reference:

> I call it my billion-dollar mistake. It was the invention of the null reference in
> 1965. At that time, I was designing the first comprehensive type system for references
> in an object-oriented language (ALGOL W). My goal was to ensure that all use of
> references should be absolutely safe, with checking performed automatically by the
> compiler. But I couldn't resist the temptation to put in a null reference, simply
> because it was so easy to implement. This has led to innumerable errors,
> vulnerabilities, and system crashes, which have probably caused a billion dollars of
> pain and damage in the last forty years.

We don't have null-values in Python, but we have `None` values. Dereferencing a `None`
value will lead to a `NameError`:

```{code-cell} python
:tags: ["raises-exception"]
xs.run()
```

With type hints we can say that this is supposed to be an integer, but the value is
missing, so we currently don't know what integer just yet:

```{code-cell} python
from typing import Optional

xs: Optional[int] = None

print(xs)
```

## Testing for optional values

We can test for optional values using `is None` or `is not None`:

```{code-cell} python
xs = None
assert xs is None
y = 42
assert y is not None
```

In addition we have a number of *falsy* values:

```{code-cell} python
assert not None
assert not 0
assert not []
assert not {}
assert not ()
assert not ""
```

## Problems with Nullable Types

Using `Optional` and nullable types in general has a lot of advantages since a compiler
or static type checker can help us avoid using optional values before we have done
proper testing first. The type `Optional[A]` is the same as `Union[A, None]` which means
that there still a few more problems:

* It's easy to forget to check for `None`, but a static type checker will help
* Extensive `None` checking can create a lot of noise in the code, increasing the
  cognitive load
* Optional types cannot be nested. How do we differ between `None` being a proper values
  and `None` for telling that the value is missing i.e `Union[None, None]`? There is no
  equivalent of e.g a list containing an empty list e.g `[[]]`.

**Example:** for dictionaries, how do we know if the key is missing or if the value is
`None`?

```{code-cell} python
mapping = dict(a=None)
mapping.get("a")
```

## Options

In functional programming we use the Option (or Maybe) type instead of `None` and
`null`. The Option type is used when a value could be missing, that is when an actual
value might not exist for a named value or variable.

An Option has an underlying type and can hold a value of that type `Some(value)`, or it
might not have the value and be `Nothing`.


The Expression library provides an `option` module in the `expression` package:

```{code-cell} python
from expression import Option, option, Some, Nothing
```

## Create option values

Create some values using the `Some` constructor:

```{code-cell} python
from expression import Some

xs = Some(42)
print(xs)
```

You should not normally want to retrieve the value of an option since you do not know if
it's successful or not. But if you are sure it's `Some` value then you retrieve the
value back using the `value` property:

```python
from expression import Some

xs = Some(42)
assert isinstance(xs, Some) # important!
xs.value
```

To create the `Nothing` case, you should use the `Nothing` singleton value. In the same
way as with `None`, this value will never change, so it's safe to re-use it for all the
code you write.

```{code-cell} python
from expression import Nothing

xs = Nothing
print(xs)
```

To test if an option is nothing you use `is` test:

```{code-cell} python
xs = Nothing
assert xs is Nothing
```

## Option returning functions

Values are great, but the real power of options comes when you create option returning
functions

```{code-cell} python
def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)

    return Nothing
```

```{code-cell} python
keep_positive(42)
```

```{code-cell} python
keep_positive(-1)
```

We can now make pure functions of potentially unsafe operations, i.e no more exceptions:

```{code-cell} python
def divide(a: float, divisor: float) -> Option[int]:
    try:
        return Some(a/divisor)
    except ZeroDivisionError:
        return Nothing
```

```{code-cell} python
divide(42, 2)
```

```{code-cell} python
divide(10, 0)
```

## Transforming option values

The great thing with options is that we can transform them without looking into the box.
This eliminates the need for error checking at every step.

```{code-cell} python
from expression import Some, option, pipe, Nothing

xs = Some(42)
ys = pipe(
    xs,
    option.map(lambda x: x*10)
)
print(ys)
```

If we map a value that is `Nothing` then the result is also `Nothing`. Nothing in,
nothing out:

```{code-cell} python
xs = Nothing
ys = pipe(
    xs,
    option.map(lambda x: x*10)
)
print(ys)
```

## Option as an effect

Effects in Expression is implemented as specially decorated coroutines ([enhanced
generators](https://www.python.org/dev/peps/pep-0342/)) using `yield`, `yield from` and
`return` to consume or generate optional values:

```{code-cell} python
from expression import effect, Some

@effect.option[int]()
def fn():
    x = yield 42
    y = yield from Some(43)

    return x + y

fn()
```

This enables ["railway oriented programming"](https://fsharpforfunandprofit.com/rop/),
e.g., if one part of the function yields from `Nothing` then the function is
side-tracked (short-circuit) and the following statements will never be executed. The
end result of the expression will be `Nothing`. Thus results from such an option
decorated function can either be `Ok(value)` or `Error(error_value)`.

```{code-cell} python
from expression import effect, Some, Nothing

@effect.option[int]()
def fn():
    x = yield from Nothing # or a function returning Nothing

    # -- The rest of the function will never be executed --
    y = yield from Some(43)

    return x + y

fn()
```

For more information about options:

- [API reference](https://expression.readthedocs.io/en/latest/reference/option.html)