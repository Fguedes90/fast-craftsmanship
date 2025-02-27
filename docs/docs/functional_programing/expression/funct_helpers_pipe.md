Pipe

Pipe module.

Contains pipe function including necessary overloads to get the type-hints right.

Example

from expression import pipe


v = 1

fn = lambda x: x + 1

gn = lambda x: x * 2


assert pipe(v, fn, gn) == gn(fn(v))

class PipeMixin

A pipe mixin class that enabled a class to use pipe fluently.

pipe(*args: Any) → Any

        Pipe the left side object through the given functions.

pipe(value: Any, *fns: Callable[[Any], Any]) → Any

Functional pipe (|>).

Allows the use of function argument on the left side of the function.

Example

pipe(x, fn) == fn(x)  # Same as x |> fn

pipe(x, fn, gn) == gn(fn(x))  # Same as x |> fn |> gn


starpipe(args: Any, /, *fns: Callable[[...], Any]) → Any

Functional pipe_n (||>, ||>, |||>, etc).

Allows the use of function arguments on the left side of the function. Calls the function with tuple arguments unpacked.

Example

starpipe((x, y), fn) == fn(x, y)  # Same as (x, y) ||> fn

starpipe((x, y), fn, gn) == gn(*fn(x))  # Same as (x, y) ||> fn |||> gn

starpipe((x, y), fn, gn, hn) == hn(*gn(*fn(x)))  # Same as (x, y) ||> fn |||> gn ||> hn
