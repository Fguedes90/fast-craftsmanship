Block

A frozen immutable list module.

This module provides an immutable list type Block and a set of useful methods and functions for working with the list.

Named “Block” to avoid conflicts with the builtin Python List type.

A Block is actually backed by a Python tuple. Tuples in Python are immutable and gives us a high performant implementation of immutable lists.

Example

xs = block.of_list([1, 2, 3, 4, 5])

ys = block.empty.cons(1).cons(2).cons(3).cons(4).cons(5)

zs = pipe(

    xs,

    block.filter(lambda x: x<10)

)

class Block(value: Iterable[_TSource] = ())

Immutable list type.

Is faster than List for prepending, but slower for appending.

Count: 200K:

| Operation | Block      | List   |
|-----------|------------|--------|
| Append    | 3.29 s     | 0.02 s |
| Prepend   | 0.05 s     | 7.02 s |

Example

xs = Cons(5, Cons(4, Cons(3, Cons(2, Cons(1, Nil)))))

ys = empty.cons(1).cons(2).cons(3).cons(4).cons(5)

append(other: Block[_TSource]) → Block[_TSource]

    Append other block to end of the block.

choose(chooser: Callable[[_TSource], Option[_TResult]]) → Block[_TResult]

    Choose items from the list.

    Applies the given function to each element of the list. Returns the list comprised of the results x for each element where the function returns Some(x).

    Parameters:

        chooser – The function to generate options from the elements.
    Returns:

        The list comprising the values selected from the chooser function.

collect(mapping: Callable[[_TSource], Block[_TResult]]) → Block[_TResult]

    Collect items from the list.

    Applies the given function to each element of the list and concatenates all the resulting sequences. This function is known as bind or flat_map in other languages.

    Parameters:

        mapping – The function to generate sequences from the elements.
    Returns:

        A list comprising the concatenated values from the mapping function.

cons(element: _TSource) → Block[_TSource]

    Add element to front of list.

dict() → list[_TSource]

    Returns a json serializable representation of the list.

static empty() → Block[Any]

    Returns empty list.

filter(predicate: Callable[[_TSource], bool]) → Block[_TSource]

    Filter list.

    Returns a new collection containing only the elements of the collection for which the given predicate returns True.

    Parameters:

        predicate – The function to test the input elements.
    Returns:

        A list containing only the elements that satisfy the predicate.

fold(folder: Callable[[_TState, _TSource], _TState], state: _TState) → _TState

    Fold block.

    Applies a function to each element of the collection, threading an accumulator argument through the computation. Take the second argument, and apply the function to it and the first element of the list. Then feed this result into the function along with the second element and so on. Return the final result. If the input function is f and the elements are i0…iN then computes f (… (f s i0) i1 …) iN.

    Parameters:

            folder – The function to update the state given the input elements.

            state – The initial state.

    Returns:

        Partially applied fold function that takes the source list and returns the final state value.

forall(predicate: Callable[[_TSource], bool]) → bool

    For all elements in block.

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

indexed(start: int = 0) → Block[tuple[int, _TSource]]

    Index elements in block.

    Returns a new list whose elements are the corresponding elements of the input list paired with the index (from start) of each element.

    Parameters:

        start – Optional index to start from. Defaults to 0.
    Returns:

        The list of indexed elements.

is_empty() → bool

    Return True if list is empty.

item(index: int) → _TSource

    Indexes into the list. The first element has index 0.

    Parameters:

        index – The index to retrieve.
    Returns:

        The value at the given index.

map(mapping: Callable[[_TSource], _TResult]) → Block[_TResult]

    Map list.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection.

    Parameters:

        mapping – The function to transform elements from the input list.
    Returns:

        The list of transformed elements.

mapi(mapping: Callable[[int, _TSource], _TResult]) → Block[_TResult]

    Map list with index.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection. The integer index passed to the function indicates the index (from 0) of element being transformed.

    Parameters:

        mapping – The function to transform elements and their indices.
    Returns:

        The list of transformed elements.

static of(*args: _TSource) → Block[_TSource]

    Create list from a number of arguments.

static of_seq(xs: Iterable[_TResult]) → Block[_TResult]

    Create list from iterable sequence.

partition(predicate: Callable[[_TSource], bool]) → tuple[Block[_TSource], Block[_TSource]]

    Partition block.

    Splits the collection into two collections, containing the elements for which the given predicate returns True and False respectively. Element order is preserved in both of the created lists.

    Parameters:

        predicate – The function to test the input elements.
    Returns:

        A list containing the elements for which the predicate evaluated to true and a list containing the elements for which the predicate evaluated to false.

reduce(reduction: Callable[[_TSource, _TSource], _TSource]) → _TSource

    Reduce block.

    Apply a function to each element of the collection, threading an accumulator argument through the computation. Apply the function to the first two elements of the list. Then feed this result into the function along with the third element and so on. Return the final result. If the input function is f and the elements are i0…iN then computes f (… (f i0 i1) i2 …) iN.

    Parameters:

            reduction – The function to reduce two list elements to a

            element. (single)

    Returns:

        Returns the final state value.

skip(count: int) → Block[_TSource]

    Returns the list after removing the first N elements.

    Parameters:

        count – The number of elements to skip.
    Returns:

        The list after removing the first N elements.

sort(reverse: bool = False) → Block[_TSourceSortable]

    Sort list directly.

    Returns a new sorted collection.

    Parameters:

        reverse – Sort in reversed order.
    Returns:

        A sorted list.

sort_with(func: Callable[[_TSource], Any], reverse: bool = False) → Block[_TSource]

    Sort list with supplied function.

    Returns a new sorted collection.

    Parameters:

            func – The function to extract a comparison key from each element in list.

            reverse – Sort in reversed order.

    Returns:

        A sorted list.

starmap(mapping: Callable[[Unpack], _TResult]) → Block[_TResult]

    Starmap source sequence.

    Unpack arguments grouped as tuple elements. Builds a new collection whose elements are the results of applying the given function to the unpacked arguments to each of the elements of the collection.

    Parameters:

        mapping – A function to transform items from the input sequence.
    Returns:

        Partially applied map function.

tail() → Block[_TSource]

    Return tail of List.

take(count: int) → Block[_TSource]

    Returns the first N elements of the list.

    Parameters:

        count – The number of items to take.
    Returns:

        The result list.

take_last(count: int) → Block[_TSource]

    Take last elements from block.

    Returns a specified number of contiguous elements from the end of the list.

    Parameters:

        count – The number of items to take.
    Returns:

        The result list.

try_head() → Option[_TSource]

    Try to get head of block.

    Returns the first element of the list, or None if the list is empty.

static unfold(generator: Callable[[_TState], Option[tuple[_TSource, _TState]]], state: _TState) → Block[_TSource]

    Unfold block.

    Returns a list that contains the elements generated by the given computation. The given initial state argument is passed to the element generator.

    Parameters:

            generator – A function that takes in the current state and returns an option tuple of the next element of the list and the next state value.

            state – The initial state.

    Returns:

        The result list.

zip(other: Block[_TResult]) → Block[tuple[_TSource, _TResult]]

        Zip block.

        Combines the two lists into a list of pairs. The two lists must have equal lengths. .

        Parameters:

            other – The second input list.
        Returns:

            A single list containing pairs of matching elements from the input lists.

collect(source: Block[_TSource], mapping: Callable[[_TSource], Block[_TResult]]) → Block[_TResult]

    Collect items from the list.

    Applies the given function to each element of the list and concatenates all the resulting sequences. This function is known as bind or flat_map in other languages.

    Parameters:

            source – The input list (curried flipped).

            mapping – The function to generate sequences from the elements.

    Returns:

        A sequence comprising the concatenated values from the mapping function.

concat(sources: Iterable[Block[_TSource]]) → Block[_TSource]

    Concatenate sequence of Block’s.

empty: Block[Any] = []

    The empty list.

filter(source: Block[_TSource], predicate: Callable[[_TSource], bool]) → Block[_TSource]

    Filter elements in block.

    Returns a new collection containing only the elements of the collection for which the given predicate returns True.

    Parameters:

            source – The input block to filter.

            predicate – The function to test the input elements.

    Returns:

        Partially applied filter function.

fold(source: Block[_TSource], folder: Callable[[_TState, _TSource], _TState], state: _TState) → _TState

    Fold elements in block.

    Applies a function to each element of the collection, threading an accumulator argument through the computation. Take the second argument, and apply the function to it and the first element of the list. Then feed this result into the function along with the second element and so on. Return the final result. If the input function is f and the elements are i0…iN then computes f (… (f s i0) i1 …) iN.

    Parameters:

            source – The input block to fold.

            folder – The function to update the state given the input elements.

            state – The initial state.

    Returns:

        Partially applied fold function that takes the source list and returns the final state value.

head(source: Block[_TSource]) → _TSource

    Returns the first element of the list.

    Parameters:

        source – The input list.
    Returns:

        The first element of the list.
    Raises:

        ValueError – Thrown when the list is empty.

indexed(source: Block[_TSource]) → Block[tuple[int, _TSource]]

    Index elements in block.

    Returns a new list whose elements are the corresponding elements of the input list paired with the index (from 0) of each element.

    Returns:

        The list of indexed elements.

is_empty(source: Block[Any]) → bool

    Returns True if the list is empty, False otherwise.

item(source: Block[_TSource], index: int) → _TSource

    Indexes into the list. The first element has index 0.

    Parameters:

            source – The input block list.

            index – The index to retrieve.

    Returns:

        The value at the given index.

map(source: Block[_TSource], mapper: Callable[[_TSource], _TResult]) → Block[_TResult]

    Map list.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection.

    Parameters:

            source – The input list (curried flipped).

            mapper – The function to transform elements from the input list.

    Returns:

        The list of transformed elements.

mapi(source: Block[_TSource], mapper: Callable[[int, _TSource], _TResult]) → Block[_TResult]

    Map list with index.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection. The integer index passed to the function indicates the index (from 0) of element being transformed.

    Parameters:

            source – The source block to map

            mapper – The function to transform elements and their indices.

    Returns:

        The list of transformed elements.

of_seq(xs: Iterable[_TSource]) → Block[_TSource]

    Create list from iterable sequence.

partition(source: Block[_TSource], predicate: Callable[[_TSource], bool]) → tuple[Block[_TSource], Block[_TSource]]

    Partition block.

    Splits the collection into two collections, containing the elements for which the given predicate returns True and False respectively. Element order is preserved in both of the created lists.

    Parameters:

            source – The source block to partition (curried flipped)

            predicate – The function to test the input elements.

    Returns:

        A list containing the elements for which the predicate evaluated to true and a list containing the elements for which the predicate evaluated to false.

skip(source: Block[_TSource], count: int) → Block[_TSource]

    Returns the list after removing the first N elements.

    Parameters:

            source – Source block to skip elements from.

            count – The number of elements to skip.

    Returns:

        The list after removing the first N elements.

skip_last(source: Block[_TSource], count: int) → Block[_TSource]

    Returns the list after removing the last N elements.

    Parameters:

            source – The source block to skip from.

            count – The number of elements to skip.

    Returns:

        The list after removing the last N elements.

sort(source: Block[_TSourceSortable], reverse: bool = False) → Block[_TSourceSortable]

    Returns a new sorted collection.

    Parameters:

            source – The source block to sort.

            reverse – Sort in reversed order.

    Returns:

        Partially applied sort function.

sort_with(source: Block[_TSource], func: Callable[[_TSource], Any], reverse: bool = False) → Block[_TSource]

    Returns a new collection sorted using “func” key function.

    Parameters:

            source – The source block to sort.

            func – The function to extract a comparison key from each element in list.

            reverse – Sort in reversed order.

    Returns:

        Partially applied sort function.

take(source: Block[_TSource], count: int) → Block[_TSource]

    Returns the first N elements of the list.

    Parameters:

            source – The input blcok to take elements from.

            count – The number of items to take.

    Returns:

        The result list.

take_last(source: Block[_TSource], count: int) → Block[_TSource]

    Take last elements from block.

    Returns a specified number of contiguous elements from the end of the list.

    Parameters:

            source – The input block to take elements from.

            count – The number of items to take.

    Returns:

        The result list.

try_head(source: Block[_TSource]) → Option[_TSource]

    Try to get the first element from the list.

    Returns the first element of the list, or None if the list is empty.

    Parameters:

        source – The input list.
    Returns:

        The first element of the list or Nothing.

unfold(state: _TState, generator: Callable[[_TState], Option[tuple[_TSource, _TState]]]) → Block[_TSource]

    Unfold block.

    Returns a list that contains the elements generated by the given computation. The given initial state argument is passed to the element generator.

    Parameters:

            generator – A function that takes in the current state and returns an option tuple of the next element of the list and the next state value.

            state – The initial state.

    Returns:

        The result list.

zip(source: Block[_TSource], other: Block[_TResult]) → Block[tuple[_TSource, _TResult]]

    Zip block with other.

    Combines the two lists into a list of pairs. The two lists must have equal lengths.

    Parameters:

            source – The input block to zip with other.

            other – The second input list.

    Returns:

        Paritally applied zip function that takes the source list and returns s single list containing pairs of matching elements from the input lists.

