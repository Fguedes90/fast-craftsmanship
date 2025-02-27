Misc
flip(fn: Callable[[_A, _B], _TResult]) → Callable[[_B, _A], _TResult]

Flips the arguments for a function taking two arguments.

Example

fn(a, b) == flip(fn)(b, a)

fst(value: tuple[_TSource, Any]) → _TSource

    Return first argument of the tuple.

identity(value: _A) → _A

    Identity function.

    Returns value given as argument.

snd(value: tuple[Any, _TSource]) → _TSource

    Return second argument of the tuple.
