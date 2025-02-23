Result

Result module.

The Result[TSource,TError] type lets you write error-tolerant code that can be composed. The Result type is typically used in monadic error-handling, which is often referred to as Railway-oriented Programming.

There is also a simplified alias of this type called Try that pins the Result type to Exception.

class Result(**kwargs: Any)

The result class.

static Error(error: _TError) → Result[_TSourceOut, _TError]

    Create a new Error result.

static Ok(value: _TResult) → Result[_TResult, _TErrorOut]

    Create a new Ok result.

bind(mapper: Callable[[_TSourceOut], Result[_TResult, _TErrorOut]]) → Result[_TResult, _TErrorOut]

    Bind result.

    Return a result of the value after applying the mapping function, or Error if the input is Error.

default_value(value: _TSource) → _TSourceOut | _TSource

    Get with default value.

    Gets the value of the result if the result is Ok, otherwise returns the specified default value.

default_with(getter: Callable[[_TErrorOut], _TSource]) → _TSource | _TSourceOut

    Get with default value lazily.

    Gets the value of the result if the result is Ok, otherwise returns the value produced by the getter

dict() → dict[str, _TSourceOut | _TErrorOut | Literal['ok', 'error']]

    Return a json serializable representation of the result.

filter(predicate: Callable[[_TSourceOut], bool], default: _TError) → Result[_TSourceOut, _TError | _TErrorOut]

    Filter result.

    Returns the input if the predicate evaluates to true, otherwise returns the default

filter_with(predicate: Callable[[_TSourceOut], bool], default: Callable[[_TSourceOut], _TErrorOut]) → Result[_TSourceOut, _TErrorOut]

    Filter result.

    Returns the input if the predicate evaluates to true, otherwise returns the default using the value as input

is_error() → bool

    Returns True if the result is an Error value.

is_ok() → bool

    Return True if the result is an Ok value.

map(mapper: Callable[[_TSourceOut], _TResult]) → Result[_TResult, _TErrorOut]

    Map result.

    Return a result of the value after applying the mapping function, or Error if the input is Error.

map2(other: Result[_TOther, _TErrorOut], mapper: Callable[[_TSourceOut, _TOther], _TResult]) → Result[_TResult, _TErrorOut]

    Map result.

    Return a result of the value after applying the mapping function, or Error if the input is Error.

map_error(mapper: Callable[[_TErrorOut], _TResult]) → Result[_TSourceOut, _TResult]

    Map error.

    Return a result of the error value after applying the mapping function, or Ok if the input is Ok.

merge() → _TSource

    Merge the ok and error values into a single value.

    This method is only available on Results where _TSource and _TError are the same type.

classmethod of_option(value: Option[_TSource], error: _TError) → Result[_TSource, _TError]

    Convert option to a result.

classmethod of_option_with(value: Option[_TSource], error: Callable[[], _TError]) → Result[_TSource, _TError]

    Convert option to a result.

or_else(other: Result[_TSourceOut, _TErrorOut]) → Result[_TSourceOut, _TErrorOut]

    Return the result if it is Ok, otherwise return the other result.

or_else_with(other: Callable[[_TErrorOut], Result[_TSourceOut, _TErrorOut]]) → Result[_TSourceOut, _TErrorOut]

    Return the result if it is Ok, otherwise return the result of the other function.

swap() → Result[_TErrorOut, _TSourceOut]

    Swaps the value in the result so an Ok becomes an Error and an Error becomes an Ok.

to_option() → Option[_TSourceOut]

        Convert result to an option.

default_value(value: _TSource) → Callable[[Result[_TSource, Any]], _TSource]

    Get the value or default value.

    Gets the value of the result if the result is Ok, otherwise returns the specified default value.

default_with(getter: Callable[[_TError], _TSource]) → Callable[[Result[_TSource, _TError]], _TSource]

    Get with default value lazily.

    Gets the value of the option if the option is Some, otherwise returns the value produced by the getter

is_error(result: Result[_TSource, _TError]) → TypeGuard[Result[_TSource, _TError]]

    Returns True if the result is an Error value.

is_ok(result: Result[_TSource, _TError]) → TypeGuard[Result[_TSource, _TError]]

    Returns True if the result is an Ok value.

swap(result: Result[_TSource, _TError]) → Result[_TError, _TSource]

    Swaps the value in the result so an Ok becomes an Error and an Error becomes an Ok.
