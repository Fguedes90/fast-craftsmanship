Pipeline
Option
pipeline() → Callable[[_A], Option[_A]]
pipeline(__fn: Callable[[_A], Option[_B]]) → Callable[[_A], Option[_B]]
pipeline(__fn1: Callable[[_A], Option[_B]], __fn2: Callable[[_B], Option[_C]]) → Callable[[_A], Option[_C]]
pipeline(__fn1: Callable[[_A], Option[_B]], __fn2: Callable[[_B], Option[_C]], __fn3: Callable[[_C], Option[_D]]) → Callable[[_A], Option[_D]]
pipeline(__fn1: Callable[[_A], Option[_B]], __fn2: Callable[[_B], Option[_C]], __fn3: Callable[[_C], Option[_D]], __fn4: Callable[[_D], Option[_E]]) → Callable[[_A], Option[_E]]
pipeline(__fn1: Callable[[_A], Option[_B]], __fn2: Callable[[_B], Option[_C]], __fn3: Callable[[_C], Option[_D]], __fn4: Callable[[_D], Option[_E]], __fn5: Callable[[_E], Option[_F]]) → Callable[[_A], Option[_F]]
pipeline(__fn1: Callable[[_A], Option[_B]], __fn2: Callable[[_B], Option[_C]], __fn3: Callable[[_C], Option[_D]], __fn4: Callable[[_D], Option[_E]], __fn5: Callable[[_E], Option[_F]], __fn6: Callable[[_F], Option[_G]]) → Callable[[_A], Option[_G]]

    Pipeline multiple option returning functions left to right.

    A pipeline kleisli (>=>) composes zero or more functions into a functional composition. The functions are composed left to right. A composition of zero functions gives back the identity function.

pipeline()(x) == Some(x)

pipeline(f)(x) == f(x)

pipeline(f, g)(x) == f(x).bind(g)

pipeline(f, g, h)(x) == f(x).bind(g).bind(h)


    Returns:

        The composed functions.

Result
pipeline() → Callable[[Any], Result[Any, Any]]
pipeline(__fn: Callable[[_A], Result[_B, _TError]]) → Callable[[_A], Result[_B, _TError]]
pipeline(__fn1: Callable[[_A], Result[_B, _TError]], __fn2: Callable[[_B], Result[_C, _TError]]) → Callable[[_A], Result[_C, _TError]]
pipeline(__fn1: Callable[[_A], Result[_B, _TError]], __fn2: Callable[[_B], Result[_C, _TError]], __fn3: Callable[[_C], Result[_D, _TError]]) → Callable[[_A], Result[_D, _TError]]
pipeline(__fn1: Callable[[_A], Result[_B, _TError]], __fn2: Callable[[_B], Result[_C, _TError]], __fn3: Callable[[_C], Result[_D, _TError]], __fn4: Callable[[_D], Result[_E, _TError]]) → Callable[[_A], Result[_E, _TError]]
pipeline(__fn1: Callable[[_A], Result[_B, _TError]], __fn2: Callable[[_B], Result[_C, _TError]], __fn3: Callable[[_C], Result[_D, _TError]], __fn4: Callable[[_D], Result[_E, _TError]], __fn5: Callable[[_E], Result[_F, _TError]]) → Callable[[_A], Result[_F, _TError]]
pipeline(__fn1: Callable[[_A], Result[_B, _TError]], __fn2: Callable[[_B], Result[_C, _TError]], __fn3: Callable[[_C], Result[_D, _TError]], __fn4: Callable[[_D], Result[_E, _TError]], __fn5: Callable[[_E], Result[_F, _TError]], __fn6: Callable[[_F], Result[_G, _TError]]) → Callable[[_A], Result[_G, _TError]]

    Pipeline multiple result returning functions left to right.

    A pipeline kleisli (>=>) composes zero or more functions into a functional composition. The functions are composed left to right. A composition of zero functions gives back the identity function.

pipeline()(x) == Ok(x)

pipeline(f)(x) == f(x)

pipeline(f, g)(x) == f(x).bind(g)

pipeline(f, g, h)(x) == f(x).bind(g).bind(h)


Returns:

    The composed functions.
