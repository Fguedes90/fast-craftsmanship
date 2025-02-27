Try

Try result class.

The Try type is a simpler Result type that pins the error type to Exception.

Everything else is the same as Result, just simpler to use.

Failure(error: Exception) → Try[Any]

    The failure Try case.

    Same as result Error but with error type pinned to an exception, i.e: Error[TSource, Exception]

Success(value: _TSource) → Try[_TSource]

    The successful Try case.

    Same as result Ok but with error type pinned to an exception, i.e: Ok[TSource, Exception]

class Try(**kwargs: Any)

    Bases: Result[_TSource, Exception]

    A try result.

    Same as Result but with error type pinned to Exception. Making it simpler to use when the error type is an exception.
