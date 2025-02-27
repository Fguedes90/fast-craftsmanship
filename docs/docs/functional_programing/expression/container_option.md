Option

Option module.

Contains a collection of static methods (functions) for operating on options. All functions takes the source as the last curried argument, i.e all functions returns a function that takes the source sequence as the only argument.

Nothing: Option[Any] = Option(none=None)

Singleton Nothing object.

Since Nothing is a singleton it can be tested e.g using is:

if xs is Nothing:

    return True

class Option(**kwargs: Any)

Option class.

static Nothing() → Option[_TSourceOut]

    Create a None option.

static Some(value: _TResult) → Option[_TResult]

    Create a Some option.

bind(mapper: Callable[[_TSourceOut], Option[_TResult]]) → Option[_TResult]

    Bind option.

    Applies and returns the result of the mapper if the value is Some. If the value is Nothing then Nothing is returned.

    Parameters:

        mapper – A function that takes the value of type TSource from an option and transforms it into an option containing a value of type TResult.
    Returns:

        An option of the output type of the mapper.

default_value(value: _TSource) → _TSourceOut | _TSource

    Get with default value.

    Gets the value of the option if the option is Some, otherwise returns the specified default value.

default_with(getter: Callable[[], _TSource]) → _TSourceOut | _TSource

    Get with default value lazily.

    Gets the value of the option if the option is Some, otherwise returns the value produced by the getter

dict() → _TSourceOut | None

    Returns a json string representation of the option.

filter(predicate: Callable[[_TSourceOut], bool]) → Option[_TSourceOut]

    Filter option.

    Returns the input if the predicate evaluates to true, otherwise returns Nothing.

is_none() → bool

    Returns true if the option is Nothing.

is_some() → bool

    Returns true if the option is not Nothing.

map(mapper: Callable[[_TSourceOut], _TResult]) → Option[_TResult]

    Map option.

    Applies the mapper to the value if the option is Some, otherwise returns Nothing.

map2(mapper: Callable[[_TSourceOut, _T2], _TResult], other: Option[_T2]) → Option[_TResult]

    Map2 option.

    Applies the mapper to the values if both options are Some, otherwise returns Nothing.

static of_obj(value: _TSource) → Option[_TSource]

    Convert object to an option.

static of_optional(value: _TSource | None) → Option[_TSource]

    Convert optional value to an option.

static of_result(result: Result[_TSource, Any]) → Option[_TSource]

    Convert result to an option.

or_else(if_none: Option[_TSourceOut]) → Option[_TSourceOut]

    Returns option if it is Some, otherwise returns if_one.

or_else_with(if_none: Callable[[], Option[_TSourceOut]]) → Option[_TSourceOut]

    Or-else-with.

    Returns option if it is Some, otherwise evaluates the given function and returns the result.

starmap(mapper: Callable[[Unpack], _TResult]) → Option[_TResult]

    Starmap option.

    Applies the mapper to the values if the option is Some, otherwise returns Nothing. The tuple is unpacked before applying the mapper.

to_list() → list[_TSourceOut]

    Convert option to list.

to_optional() → _TSourceOut | None

    Convert option to an optional.

to_result(error: _TError) → Result[_TSourceOut, _TError]

    Convert option to a result.

to_result_with(error: Callable[[], _TError]) → Result[_TSourceOut, _TError]

    Convert option to a result.

to_seq() → Seq[_TSourceOut]

    Convert option to sequence.

property value: _TSourceOut

        Returns the value wrapped by the option.

        A ValueError is raised if the option is Nothing.

Some(value: _T1) → Option[_T1]

    Create a Some option.

bind(option: Option[_TSource], mapper: Callable[[_TSource], Option[_TResult]]) → Option[_TResult]

    Bind option.

    Applies and returns the result of the mapper if the value is Some. If the value is Nothing then Nothing is returned.

    Parameters:

            option – Source option to bind.

            mapper – A function that takes the value of type _TSource from an option and transforms it into an option containing a value of type TResult.

    Returns:

        A partially applied function that takes an option and returns an option of the output type of the mapper.

default_arg(value: Option[_TSource], default_value: _T1) → _TSource | _T1

    Specify default argument.

    Used to specify a default value for an optional argument in the implementation of a function. Same as default_value, but “uncurried” and with the arguments swapped.

default_value(option: Option[_TSource], value: _T1) → _TSource | _T1

    Get value or default value.

    Gets the value of the option if the option is Some, otherwise returns the specified default value.

default_with(getter: Callable[[], _TSource]) → Callable[[Option[_TSource]], _TSource]

    Get with default value lazily.

    Gets the value of the option if the option is Some, otherwise returns the value produced by the getter

of_obj(value: Any) → Option[Any]

    Convert object to an option.

    Convert a value that could be None into an Option value.

    Parameters:

        value – The input object.
    Returns:

        The result option.

of_optional(value: _TSource | None) → Option[_TSource]

    Convert an optional value to an option.

    Parameters:

        value – The input optional value.
    Returns:

        The result option.

or_else(option: Option[_TSource], if_none: Option[_TSource]) → Option[_TSource]

    Returns option if it is Some, otherwise returns if_none.

to_optional(value: Option[_TSource]) → _TSource | None

    Convert an option value to an optional.

    Parameters:

        value – The input option value.
    Returns:

        The result optional.


