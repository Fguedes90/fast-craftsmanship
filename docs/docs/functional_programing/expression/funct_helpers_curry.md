Curry
curry(num_args: Literal[0]) → Callable[[Callable[[_P], _B]], Callable[[_P], _B]]
curry(num_args: Literal[1]) → Callable[[Callable[[Concatenate[_A, _P]], _B]], Callable[[_A], Callable[[_P], _B]]]
curry(num_args: Literal[2]) → Callable[[Callable[[Concatenate[_A, _B, _P]], _C]], Callable[[_A], Callable[[_B], Callable[[_P], _C]]]]
curry(num_args: Literal[3]) → Callable[[Callable[[Concatenate[_A, _B, _C, _P]], _D]], Callable[[_A], Callable[[_B], Callable[[_C], Callable[[_P], _D]]]]]
curry(num_args: Literal[4]) → Callable[[Callable[[Concatenate[_A, _B, _C, _D, _P]], _E]], Callable[[_A], Callable[[_B], Callable[[_C], Callable[[_D], Callable[[_P], _E]]]]]]

    A curry decorator.

    Makes a function curried.

    Parameters:

            num_args – The number of args to curry from the start of the

            function

    Example

@curry(1)

def add(a: int, b: int) -> int:

   return a + b


assert add(3)(4) == 7

curry_flip(num_args: Literal[0]) → Callable[[Callable[[_P], _A]], Callable[[_P], _A]]
curry_flip(num_args: Literal[1]) → Callable[[Callable[[Concatenate[_A, _P]], _B]], Callable[[_P], Callable[[_A], _B]]]
curry_flip(num_args: Literal[2]) → Callable[[Callable[[Concatenate[_A, _B, _P]], _C]], Callable[[_P], Callable[[_A], Callable[[_B], _C]]]]
curry_flip(num_args: Literal[3]) → Callable[[Callable[[Concatenate[_A, _B, _C, _P]], _D]], Callable[[_P], Callable[[_A], Callable[[_B], Callable[[_C], _D]]]]]
curry_flip(num_args: Literal[4]) → Callable[[Callable[[Concatenate[_A, _B, _C, _D, _P]], _E]], Callable[[_P], Callable[[_A], Callable[[_B], Callable[[_C], Callable[[_D], _E]]]]]]

    A flipped curry decorator.

    Makes a function curried, but flips the curried arguments to become the last arguments. This is very nice when having e.g optional arguments after a source argument that will be piped.

    Parameters:

            num_args – The number of args to curry from the start of the

            function

    Example

@curry_flip(1)

def map(source: List[int], mapper: Callable[[int], int]):

   return [mapper(x) for x in source]


ys = pipe(xs, map(lambda x: x * 10))