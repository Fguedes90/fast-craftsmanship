
# Expression

## Getting Started

You can install the latest `expression` from PyPI by running `pip` (or
`pip3`). Note that `expression` only works for Python 3.10+.

```console
> pip install expression
```

To add Pydantic v2 support, install the `pydantic` extra:

```console
> pip install expression[pydantic]
```


## Goals

- Industrial strength library for functional programming in Python.
- The resulting code should look and feel like Python
  ([PEP-8](https://www.python.org/dev/peps/pep-0008/)). We want to make a
  better Python, not some obscure DSL or academic Monad tutorial.
- Provide pipelining and pipe friendly methods. Compose all the things!
- Dot-chaining on objects as an alternative syntax to pipes.
- Lower the cognitive load on the programmer by:
  - Avoid currying, not supported in Python by default and not a well known
    concept by Python programmers.
  - Avoid operator (`|`, `>>`, etc) overloading, this usually confuses more
    than it helps.
  - Avoid recursion. Recursion is not normally used in Python and any use of it
    should be hidden within the SDK.
- Provide [type-hints](https://docs.python.org/3/library/typing.html) for all
  functions and methods.
- Support PEP 634 and structural pattern matching.
- Code must pass strict static type checking by
  [Pylance](https://devblogs.microsoft.com/python/announcing-pylance-fast-feature-rich-language-support-for-python-in-visual-studio-code/).
  Pylance is awesome, use it!
- [Pydantic](https://pydantic-docs.helpmanual.io/) friendly data types. Use Expression
  types as part of your Pydantic data model and (de)serialize to/from JSON.


## Supported features

Expression will never provide you with all the features of F# and .NET. We are
providing a few of the features we think are useful, and will add more
on-demand as we go along.

- **Pipelining** - for creating workflows.
- **Composition** - for composing and creating new operators.
- **Fluent or Functional** syntax, i.e., dot chain or pipeline operators.
- **Pattern Matching** - an alternative flow control to `if-elif-else`.
- **Error Handling** - Several error handling types.
  - **Option** - for optional stuff and better `None` handling.
  - **Result** - for better error handling and enables railway-oriented
    programming in Python.
  - **Try** - a simpler result type that pins the error to an Exception.
- **Collections** - immutable collections.
  - **TypedArray** - a generic array type that abstracts the details of
    `bytearray`, `array.array` and `list` modules.
  - **Sequence** - a better
    [itertools](https://docs.python.org/3/library/itertools.html) and
    fully compatible with Python iterables.
  - **Block** - a frozen and immutable list type.
  - **Map** - a frozen and immutable dictionary type.
  - **AsyncSeq** - Asynchronous iterables.
  - **AsyncObservable** - Asynchronous observables. Provided separately
    by [aioreactive](https://github.com/dbrattli/aioreactive).
- **Data Modeling** - sum and product types
  - **@tagged_union** - A tagged (discriminated) union type decorator.
- **Parser Combinators** - A recursive decent string parser combinator
  library.
- **Effects**: - lightweight computational expressions for Python. This
  is amazing stuff.
  - **option** - an optional world for working with optional values.
  - **result** - an error handling world for working with result values.
- **Mailbox Processor**: for lock free programming using the [Actor
  model](https://en.wikipedia.org/wiki/Actor_model).
- **Cancellation Token**: for cancellation of asynchronous (and
  synchronous) workflows.
- **Disposable**: For resource management.


### Pipelining

Expression provides a `pipe` function similar to `|>` in F#. We don't want to overload
any Python operators, e.g., `|` so `pipe` is a plain old function taking N-arguments,
and will let you pipe a value through any number of functions.

```python
from collections.abc import Callable

from expression import pipe


v = 1
fn1: Callable[[int], int] = lambda x: x + 1
gn1: Callable[[int], int] = lambda x: x * 2

assert pipe(v, fn1, gn1) == gn1(fn1(v))
```

Expression objects (e.g., `Some`, `Seq`, `Result`) also have a `pipe` method, so you can
dot chain pipelines directly on the object:

```python
from expression import Option, Some


v = Some(1)
fn2: Callable[[Option[int]], Option[int]] = lambda x: x.map(lambda y: y + 1)
gn2: Callable[[Option[int]], Option[int]] = lambda x: x.map(lambda y: y * 2)

assert v.pipe(fn2, gn2) == gn2(fn2(v))
```

So for example with sequences you may create sequence transforming
pipelines:

```python
from collections.abc import Callable

from expression.collections import Seq, seq


# Since static type checkes aren't good good at inferring lambda types
mapper: Callable[[int], int] = lambda x: x * 10
predicate: Callable[[int], bool] = lambda x: x > 100
folder: Callable[[int, int], int] = lambda s, x: s + x

xs = Seq.of(9, 10, 11)
ys = xs.pipe(
    seq.map(mapper),
    seq.filter(predicate),
    seq.fold(folder, 0),
)

assert ys == 110
```

### Composition

Functions may even be composed directly into custom operators:

```python
from expression import compose
from expression.collections import Seq, seq


mapper: Callable[[int], int] = lambda x: x * 10
predicate: Callable[[int], bool] = lambda x: x > 100
folder: Callable[[int, int], int] = lambda s, x: s + x

xs = Seq.of(9, 10, 11)
custom = compose(
    seq.map(mapper),
    seq.filter(predicate),
    seq.fold(folder, 0),
)
ys = custom(xs)

assert ys == 110
```

### Fluent and Functional

Expression can be used both with a fluent or functional syntax (or both.)

#### Fluent syntax

The fluent syntax uses methods and is very compact. But it might get you into trouble
for large pipelines since it's not a natural way of adding line breaks.

```python
from expression.collections import Seq


xs = Seq.of(1, 2, 3)
ys = xs.map(lambda x: x * 100).filter(lambda x: x > 100).fold(lambda s, x: s + x, 0)
```

Note that fluent syntax is probably the better choice if you use mypy for type checking
since mypy may have problems inferring types through larger pipelines.

#### Functional syntax

The functional syntax is a bit more verbose but you can easily add new operations on new
lines. The functional syntax is great to use together with pylance/pyright.

```python
from expression import pipe
from expression.collections import Seq, seq


mapper: Callable[[int], int] = lambda x: x * 100

xs = Seq.of(1, 2, 3)
ys = pipe(
    xs,
    seq.map(mapper),
    seq.filter(lambda x: x > 100),
    seq.fold(lambda s, x: s + x, 0),
)
```

Both fluent and functional syntax may be mixed and even pipe can be used
fluently.

```python
from expression.collections import Seq, seq


xs = Seq.of(1, 2, 3).pipe(seq.map(mapper))
```


### Option

The `Option` type is used when a function or method cannot produce a meaningful
output for a given input.

An option value may have a value of a given type, i.e., `Some(value)`, or it might
not have any meaningful value, i.e., `Nothing`.

```python
from expression import Nothing, Option, Some


def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)

    return Nothing
```

```python
from typing import Literal

from expression import Ok, Option


def exists(x: Option[int]) -> bool:
    match x:
        case Option(tag="some"):
            return True
        case _:
            return False
```

### Option as an effect

Effects in Expression is implemented as specially decorated coroutines
([enhanced generators](https://www.python.org/dev/peps/pep-0342/)) using
`yield`, `yield from` and `return` to consume or generate optional values:

```python
from collections.abc import Generator

from expression import Some, effect


@effect.option[int]()
def fn3() -> Generator[int, int, int]:
    x = yield 42
    y = yield from Some(43)

    return x + y


xs = fn3()
```

This enables ["railway oriented programming"](https://fsharpforfunandprofit.com/rop/),
e.g., if one part of the function yields from `Nothing` then the function is
side-tracked (short-circuit) and the following statements will never be executed. The
end result of the expression will be `Nothing`. Thus results from such an option
decorated function can either be `Ok(value)` or `Error(error_value)`.

```python
from collections.abc import Generator

from expression import Nothing, Some, effect


@effect.option[int]()
def fn4() -> Generator[int, int, int]:
    x = yield from Nothing  # or a function returning Nothing

    # -- The rest of the function will never be executed --
    y = yield from Some(43)

    return x + y


xs = fn4()
assert xs is Nothing
```

### Option as an applicative

In functional programming, we sometimes want to combine two Option values into a new
Option. However, this combination should only happen if both Options are Some. If either
Option is None, the resulting value should also be None.

The map2 function allows us to achieve this behavior. It takes two Option values and a
function as arguments. The function is applied only if both Options are Some, and the
result becomes the new Some value. Otherwise, map2 returns None.

This approach ensures that our combined value reflects the presence or absence of data
in the original Options.

```python
from operator import add

from expression import Nothing, Option, Some


def keep_positive(a: int) -> Option[int]:
    if a > 0:
        return Some(a)
    else:
        return Nothing


def add_options(a: Option[int], b: Option[int]):
    return a.map2(add, b)


assert add_options(keep_positive(4), keep_positive(-2)) is Nothing

assert add_options(keep_positive(3), keep_positive(2)) == Some(5)
```

For more information about options:

- [Tutorial](https://expression.readthedocs.io/en/latest/tutorial/optional_values.html)
- [API reference](https://expression.readthedocs.io/en/latest/reference/option.html)


### Result

The `Result[T, TError]` type lets you write error-tolerant code that can be composed. A
Result works similar to `Option`, but lets you define the value used for errors, e.g.,
an exception type or similar. This is great when you want to know why some operation
failed (not just `Nothing`). This type serves the same purpose of an `Either` type where
`Left` is used for the error condition and `Right` for a success value.

```python
from expression import Ok, Result, effect


@effect.result[int, Exception]()
def fn5() -> Generator[int, int, int]:
    x = yield from Ok(42)
    y = yield from Ok(10)
    return x + y


xs = fn5()
assert isinstance(xs, Result)
```

A simplified type called `Try` is also available. It's a result type that is
pinned to `Exception` i.e., `Result[TSource, Exception]`.


### Sequence

Sequences is a thin wrapper on top of iterables and contains operations for working with
Python iterables. Iterables are immutable by design, and perfectly suited for functional
programming.

```python
import functools
from collections.abc import Iterable

from expression import pipe
from expression.collections import seq


# Normal python way. Nested functions are hard to read since you need to
# start reading from the end of the expression.
xs: Iterable[int]
xs = range(100)
ys = functools.reduce(lambda s, x: s + x, filter(lambda x: x > 100, map(lambda x: x * 10, xs)), 0)

mapper: Callable[[int], int] = lambda x: x * 10
predicate: Callable[[int], bool] = lambda x: x > 100
folder: Callable[[int, int], int] = lambda s, x: s + x

# With Expression, you pipe the result, so it flows from one operator to the next:
zs: int = pipe(
    xs,
    seq.map(mapper),
    seq.filter(predicate),
    seq.fold(folder, 0),
)
assert ys == zs
```

## Tagged Unions

Tagged Unions (aka discriminated unions) may look similar to normal Python Unions. But
they are [different](https://stackoverflow.com/a/61646841) in that the operands in a
type union `(A | B)` are both types, while the cases in a tagged union type `U = A | B`
are both constructors for the type U and are not types themselves. One consequence is
that tagged unions can be nested in a way union types might not.

In Expression you make a tagged union by defining your type similar to a `dataclass` and
decorate it with `@tagged_union` and add the appropriate generic types that this union
represent for each case. Then you optionally define static or class-method constructors
for creating each of the tagged union cases.

```python
from dataclasses import dataclass
from typing import Literal

from expression import case, tag, tagged_union


@dataclass
class Rectangle:
    width: float
    length: float


@dataclass
class Circle:
    radius: float


@tagged_union
class Shape:
    tag: Literal["rectangle", "circle"] = tag()

    rectangle: Rectangle = case()
    circle: Circle = case()

    @staticmethod
    def Rectangle(width: float, length: float) -> "Shape":
        """Optional static method for creating a tagged union case"""
        return Shape(rectangle=Rectangle(width, length))

    @staticmethod
    def Circle(radius: float) -> "Shape":
        """Optional static method for creating a tagged union case"""
        return Shape(circle=Circle(radius))
```

Note that the tag field is optional, but recommended. If you don't specify a tag field
then then it will be created for you, but static type checkers will not be able to type
check correctly when pattern matching. The `tag` field if specified should be a literal
type with all the possible values for the tag. This is used by static type checkers to
check exhaustiveness of pattern matching.

Each case is given the `case()` field initializer. This is optional, but recommended for
static type checkers to work correctly. It's not required for the code to work properly,

Now you may pattern match the shape to get back the actual value:

```python
shape = Shape.Rectangle(2.3, 3.3)

match shape:
    case Shape(tag="rectangle", rectangle=Rectangle(width=2.3)):
        assert shape.rectangle.width == 2.3
    case _:
        assert False
```

Note that when matching keyword arguments, then the `tag` keyword argument must be
specified for static type checkers to check exhaustiveness correctly. It's not required
for the code to work properly, but it's recommended to avoid typing errors.
