Compose
compose() → Callable[[_A], _A]
compose(__fn1: Callable[[_A], _B]) → Callable[[_A], _B]
compose(__fn1: Callable[[_A], _B], __fn2: Callable[[_B], _C]) → Callable[[_A], _C]
compose(__fn1: Callable[[_A], _B], __fn2: Callable[[_B], _C], __fn3: Callable[[_C], _D]) → Callable[[_A], _D]
compose(fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], fn3: Callable[[_C], _D], fn4: Callable[[_D], _E], /) → Callable[[_A], _E]
compose(fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], fn3: Callable[[_C], _D], fn4: Callable[[_D], _E], fn5: Callable[[_E], _F], /) → Callable[[_A], _F]
compose(fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], fn3: Callable[[_C], _D], fn4: Callable[[_D], _E], fn5: Callable[[_E], _F], fn6: Callable[[_F], _G], /) → Callable[[_A], _G]
compose(fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], fn3: Callable[[_C], _D], fn4: Callable[[_D], _E], fn5: Callable[[_E], _F], fn6: Callable[[_F], _G], fn7: Callable[[_G], _H], /) → Callable[[_A], _H]
compose(fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], fn3: Callable[[_C], _D], fn4: Callable[[_D], _E], fn5: Callable[[_E], _F], fn6: Callable[[_F], _G], fn7: Callable[[_G], _H], fn8: Callable[[_H], _T], /) → Callable[[_A], _T]
compose(fn1: Callable[[_A], _B], fn2: Callable[[_B], _C], fn3: Callable[[_C], _D], fn4: Callable[[_D], _E], fn5: Callable[[_E], _F], fn6: Callable[[_F], _G], fn7: Callable[[_G], _H], fn8: Callable[[_H], _T], fn9: Callable[[_T], _J], /) → Callable[[_A], _J]

    Compose multiple functions left to right.

    Composes zero or more functions into a functional composition. The functions are composed left to right. A composition of zero functions gives back the identity function.

x = 42

f = lambda a: a * 10

g = lambda b: b + 3

h = lambda c: c / 2

compose()(x) == x

compose(f)(x) == f(x)

compose(f, g)(x) == g(f(x))

compose(f, g, h)(x) == h(g(f(x)))


Returns:

    The composed function.
