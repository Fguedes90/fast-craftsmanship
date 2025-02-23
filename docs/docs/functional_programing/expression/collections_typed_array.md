Typed Array

A typed array module.

This module provides an typed array type TypedArray and a set of useful methods and functions for working with the array. The internal backing storage is bytearray, array.array or list depending on type of input.

class TypedArray(initializer: Iterable[_TSource] | None = None, typecode: TypeCode | None = None)

choose(chooser: Callable[[_TSource], Option[_TResult]]) → TypedArray[_TResult]

    Choose items from the list.

    Applies the given function to each element of the list. Returns the list comprised of the results x for each element where the function returns Some(x).

    Parameters:

        chooser – The function to generate options from the elements.
    Returns:

        The list comprising the values selected from the chooser function.

classmethod empty() → TypedArray[Any]

    Returns empty array.

filter(predicate: Callable[[_TSource], bool]) → TypedArray[_TSource]

    Filter list.

    Returns a new collection containing only the elements of the collection for which the given predicate returns True.

    Parameters:

        predicate – The function to test the input elements.
    Returns:

        A list containing only the elements that satisfy the predicate.

fold(folder: Callable[[_TState, _TSource], _TState], state: _TState) → _TState

    Fold array.

    Applies a function to each element of the array, threading an accumulator argument through the computation. Take the second argument, and apply the function to it and the first element of the list. Then feed this result into the function along with the second element and so on. Return the final result. If the input function is f and the elements are i0…iN then computes f (… (f s i0) i1 …) iN.

    Parameters:

            folder – The function to update the state given the input elements.

            state – The initial state.

    Returns:

        Partially applied fold function that takes the source list and returns the final state value.

forall(predicate: Callable[[_TSource], bool]) → bool

    Test all elements.

    Tests if all elements of the collection satisfy the given predicate.

    Parameters:

        predicate – The function to test the input elements.
    Returns:

        True if all of the elements satisfy the predicate.

head() → _TSource

    Returns the first element of the list.

    Parameters:

        source – The input list.
    Returns:

        The first element of the list.
    Raises:

        ValueError – Thrown when the list is empty.

indexed(start: int = 0) → TypedArray[tuple[int, _TSource]]

    Index array elements.

    Returns a new array whose elements are the corresponding elements of the input array paired with the index (from start) of each element.

    Parameters:

        start – Optional index to start from. Defaults to 0.
    Returns:

        The list of indexed elements.

insert(index: int, value: _TSource) → None

    S.insert(index, value) – insert value before index

is_empty() → bool

    Return True if list is empty.

item(index: int) → _TSource

    Indexes into the list. The first element has index 0.

    Parameters:

        index – The index to retrieve.
    Returns:

        The value at the given index.

static of(*args: _TSource) → TypedArray[_TSource]

    Create list from a number of arguments.

static of_seq(xs: Iterable[_TSource]) → TypedArray[_TSource]

    Create list from iterable sequence.

skip(count: int) → TypedArray[_TSource]

    Returns the array after removing the first N elements.

    Parameters:

        count – The number of elements to skip.
    Returns:

        The array after removing the first N elements.

sort(reverse: bool = False) → TypedArray[_TSourceSortable]

    Sort array directly.

    Returns a new sorted collection.

    Parameters:

        reverse – Sort in reversed order.
    Returns:

        A sorted array.

sort_with(func: Callable[[_TSource], Any], reverse: bool = False) → TypedArray[_TSource]

    Sort array with supplied function.

    Returns a new sorted collection.

    Parameters:

            func – The function to extract a comparison key from each element in list.

            reverse – Sort in reversed order.

    Returns:

        A sorted array.

tail() → TypedArray[_TSource]

    Return tail of List.

take(count: int) → TypedArray[_TSource]

    Returns the first N elements of the list.

    Parameters:

        count – The number of items to take.
    Returns:

        The result list.

take_last(count: int) → TypedArray[_TSource]

    Take last elements.

    Returns a specified number of contiguous elements from the end of the list.

    Parameters:

        count – The number of items to take.
    Returns:

        The result list.

try_head() → Option[_TSource]

    Try to return first element.

    Returns the first element of the list, or None if the list is empty.

static unfold(generator: Callable[[_TState], Option[tuple[_TSource, _TState]]], state: _TState) → TypedArray[_TSource]

        Unfold array.

        Returns a list that contains the elements generated by the given computation. The given initial state argument is passed to the element generator.

        Parameters:

                generator – A function that takes in the current state and returns an option tuple of the next element of the list and the next state value.

                state – The initial state.

        Returns:

            The result list.

filter(source: TypedArray[_TSource], predicate: Callable[[_TSource], bool]) → TypedArray[_TSource]

    Filter array.

    Returns a new array containing only the elements of the array for which the given predicate returns True.

    Parameters:

            source – The source array to filter.

            predicate – The function to test the input elements.

    Returns:

        Partially applied filter function.

fold(source: TypedArray[_TSource], folder: Callable[[_TState, _TSource], _TState], state: _TState) → _TState

    Fold the array.

    Applies a function to each element of the collection, threading an accumulator argument through the computation. Take the second argument, and apply the function to it and the first element of the list. Then feed this result into the function along with the second element and so on. Return the final result. If the input function is f and the elements are i0…iN then computes f (… (f s i0) i1 …) iN.

    Parameters:

            source – The source array to fold.

            folder – The function to update the state given the input elements.

            state – The initial state.

    Returns:

        Partially applied fold function that takes the source list and returns the final state value.

is_empty(source: TypedArray[Any]) → bool

    Returns True if the list is empty, False otherwise.

map(source: TypedArray[_TSource], mapper: Callable[[_TSource], _TResult]) → TypedArray[_TResult]

    Map array.

    Builds a new array whose elements are the results of applying the given function to each of the elements of the array.

    Parameters:

            source – The source array to map.

            mapper – The function to transform elements from the input array.

    Returns:

        A new array of transformed elements.

of(*args: _TSource) → TypedArray[_TSource]

    Create list from a number of arguments.

of_seq(xs: Iterable[_TSource]) → TypedArray[_TSource]

    Create list from iterable sequence.

take(source: TypedArray[_TSource], count: int) → TypedArray[_TSource]

    Return the first N elements of the array.

    Parameters:

            source – The source array to take from.

            count – The number of items to take.

    Returns:

        The result array.

take_last(source: TypedArray[_TSource], count: int) → TypedArray[_TSource]

    Take last elements.

    Returns a specified number of contiguous elements from the end of the list.

    Parameters:

            source – The source array to take from.

            count – The number of items to take.

    Returns:

        The result list.

try_head(source: TypedArray[_TSource]) → Option[_TSource]

    Try to get the first element from the list.

    Returns the first element of the list, or None if the list is empty.

    Parameters:

        source – The input list.
    Returns:

        The first element of the list or Nothing.

unfold(state: _TState, generator: Callable[[_TState], Option[tuple[_TSource, _TState]]]) → TypedArray[_TSource]

    Unfold array.

    Returns a list that contains the elements generated by the given computation. The given initial state argument is passed to the element generator.

    Parameters:

            state – The initial state.

            generator – A function that takes in the current state and returns an option tuple of the next element of the list and the next state value.

    Returns:

        The result list.

