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

Map
class Map(_Map__tree: Option[MapTreeLeaf[_Key, _Value]] | None = None)

The immutable map class.

for_all(predicate: Callable[[_Key, _Value], bool]) → bool

    Test all elements in map.

    Returns true if the given predicate returns true for all of the bindings in the map.

    Parameters:

        predicate – The function to test the input elements.
    Returns:

        True if the predicate evaluates to true for all of the bindings in the map.

items() → a set-like object providing a view on D's items

map(mapping: Callable[[_Key, _Value], _Result]) → Map[_Key, _Result]

    Map the mapping.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection. The key passed to the function indicates the key of element being transformed.

    Parameters:

        mapping – The function to transform the key/value pairs
    Returns:

        The resulting map of keys and transformed values.

static of_block(lst: Block[tuple[_Key, _Value]]) → Map[_Key, _Value]

    Generate map from list.

    Returns:

        The new map.

static of_list(lst: list[tuple[_Key_, _Result]]) → Map[_Key_, _Result]

    Generate map from list.

    Returns:

        The new map.

static of_seq(sequence: Iterable[tuple[_Key_, _Result]]) → Map[_Key_, _Result]

    Generate map from sequence.

    Generates a new map from an iterable of key/value tuples. This is an alias for Map.create.

    Returns:

        The new map.

to_seq() → Iterable[tuple[_Key, _Value]]

        Convert to sequence.

        Returns:

            Sequence of key, value tuples.

add(table: Map[_Key, _Value], key: _Key, value: _Value) → Map[_Key, _Value]

    Add key with value to map.

    Returns a new map with the binding added to the given map. If a binding with the given key already exists in the input map, the existing binding is replaced by the new binding in the result map.

    Parameters:

            table – The input map.

            key – The input key.

            value – The input value.

    Returns:

        A partially applied add function that takes the input map and returns the output map.

change(table: Map[_Key, _Value], key: _Key, fn: Callable[[Option[_Value]], Option[_Value]]) → Map[_Key, _Value]

    Change element in map.

    Returns a new map with the value stored under key changed according to f.

    Parameters:

            key – The input key.

            fn – The change function.

            table – The input table.

    Returns:

        The input key.

count(table: Map[Any, Any]) → int

    Return the number of bindings in the map.

exists(table: Map[_Key, _Value], predicate: Callable[[_Key, _Value], bool]) → bool

    Test if element exists in map.

    Returns true if the given predicate returns true for one of the bindings in the map.

    Parameters:

            table – The input map.

            predicate – The function to test the input elements.

    Returns:

        Partially applied function that takes a map table and returns true if the predicate returns true for one of the key/value pairs.

find(table: Map[_Key, _Value], key: _Key) → _Value

    Find element with key in map.

    Lookup an element in the map, raising KeyNotFoundException if no binding exists in the map.

    Parameters:

            key – The key to find.

            table – The map to find the key in.

is_empty(table: Map[Any, Any]) → bool

    Is the map empty?

    Parameters:

        table – The input map.
    Returns:

        True if the map is empty.

of(**args: _Value) → Map[str, _Value]

    Create map from arguments.

remove(table: Map[_Key, _Value], key: _Key) → Map[_Key, _Value]

    Remove element from map.

    Removes an element from the domain of the map. No exception is raised if the element is not present.

    Parameters:

            key – The key to remove.

            table – The table to remove the key from.

    Returns:

        The resulting map.

try_find(table: Map[_Key, _Value], key: _Key) → Option[_Value]

    Try to find element with key in map.

    Lookup an element in the map, returning a Some value if the element is in the domain of the map and Nothing if not.

    Parameters:

            table – The input map.

            key – The input key.

    Returns:

        A partially applied try_find function that takes a map instance and returns the result.

try_pick(table: Map[_Key, _Value], chooser: Callable[[_Key, _Value], Option[_Result]]) → Option[_Result]

    Pick element in map.

    Searches the map looking for the first element where the given function returns a Some value.

    Parameters:

            table – The input map.

            chooser – The function to generate options from the key/value pairs.

    Returns:

        Partially applied try_pick function that takes the input map and returns the first result.

Seq

Sequence module.

Contains a collection of static methods (functions) for operating on sequences. A sequence is a thin wrapper around Iterable so all functions take (and return) Python iterables.

All functions takes the source as the last curried argument, i.e all functions returns a function that takes the source sequence as the only argument.

Example (functional style):

from expression.collections import seq

xs = seq.of_iterable([1, 2, 3])

ys = xs.pipe(
    seq.map(lambda x: x + 1),
    seq.filter(lambda x: x < 3)
)

Example (fluent style):

from expression.collections import Seq

xs = Seq([1, 2, 3])

ys = xs.map(lambda x: x + 1).filter(lambda x: x < 3)

class Seq(iterable: Iterable[_TSource] = ())

Sequence type.

Contains instance methods for dot-chaining operators methods on sequences.

Example

xs = Seq([1, 2, 3])

ys = xs.map(lambda x: x + 1).filter(lambda x: x < 3)

append(*others: Iterable[_TSource]) → Seq[_TSource]

    Append sequence to other sequences.

    Wraps the given enumerations as a single concatenated enumeration.

choose(chooser: Callable[[_TSource], Option[_TResult]]) → Seq[_TResult]

    Choose items from the sequence.

    Applies the given function to each element of the list. Returns the list comprised of the results x for each element where the function returns Some(x).

    Parameters:

        chooser – The function to generate options from the elements.
    Returns:

        The list comprising the values selected from the chooser function.

collect(mapping: Callable[[_TSource], Seq[_TResult]]) → Seq[_TResult]

    Collect items from the sequence.

    Applies the given function to each element of the list and concatenates all the resulting sequences. This function is known as bind or flat_map in other languages.

    Parameters:

        mapping – The function to generate sequences from the elements.
    Returns:

        A sequence comprising the concatenated values from the mapping function.

static delay(generator: Callable[[], Iterable[_TSource]]) → Iterable[_TSource]

    Delay sequence.

    Returns a sequence that is built from the given delayed specification of a sequence.

    The input function is evaluated each time an IEnumerator for the sequence is requested.

    Parameters:

        generator – The generating function for the sequence.

dict() → Iterable[_TSource]

    Returns a json serializable representation of the list.

static empty() → Seq[Any]

    Returns empty sequence.

fold(folder: Callable[[_TState, _TSource], _TState], state: _TState) → _TState

    Fold sequence.

    Applies a function to each element of the collection, threading an accumulator argument through the computation. If the input function is f and the elements are i0…iN then computes f (… (f s i0)…) iN.

    Parameters:

            folder – A function that updates the state with each element from the sequence.

            state – The initial state.

    Returns:

        The state object after the folding function is applied to each element of the sequence.

head() → _TSource

    Returns the first element of the sequence.

length() → int

    Returns the length of the sequence.

map(mapper: Callable[[_TSource], _TResult]) → Seq[_TResult]

    Map sequence.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection.

    Parameters:

        mapper – A function to transform items from the input sequence.
    Returns:

        The result sequence.

mapi(mapping: Callable[[int, _TSource], _TResult]) → Seq[_TResult]

    Map list with index.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection. The integer index passed to the function indicates the index (from 0) of element being transformed.

    Parameters:

        mapping – The function to transform elements and their indices.
    Returns:

        The list of transformed elements.

scan(scanner: Callable[[_TState, _TSource], _TState], state: _TState) → Iterable[_TState]

    Scan sequence.

    Like fold, but computes on-demand and returns the sequence of intermediary and final results.

    Parameters:

            scanner – A function that updates the state with each element from the sequence.

            state – The initial state.

    Returns:

        The resulting sequence of computed states.

skip(count: int) → Seq[_TSource]

    Skip elements from sequence.

    Returns a sequence that skips N elements of the underlying sequence and then yields the remaining elements of the sequence.

    Parameters:

        count – The number of items to skip.

starmap(mapping: Callable[[_T1, _T2], _TResult]) → Seq[_TResult]

starmap(mapping: Callable[[_T1, _T2, _T3], _TResult]) → Seq[_TResult]
starmap(mapping: Callable[[_T1, _T2, _T3, _T4], _TResult]) → Seq[_TResult]

    Starmap source sequence.

    Unpack arguments grouped as tuple elements. Builds a new collection whose elements are the results of applying the given function to the unpacked arguments to each of the elements of the collection.

    Parameters:

        mapping – A function to transform items from the input sequence.
    Returns:

        Partially applied map function.

sum() → _TSupportsSum

    Returns the sum of the elements in the sequence.

sum_by(projection: Callable[[_TSource], _TSupportsSum]) → _TSupportsSum

    Sum the sequence by projection.

    Returns the sum of the results generated by applying the function to each element of the sequence.

tail() → Seq[_TSource]

    Return the tail of the sequence.

    Returns a sequence that skips 1 element of the underlying sequence and then yields the remaining elements of the sequence.

take(count: int) → Seq[_TSource]

    Returns the first N elements of the sequence.

    Parameters:

        count – The number of items to take.

classmethod unfold(generator: Callable[[_TState], Option[tuple[_TSource, _TState]]], state: _TState) → Iterable[_TSource]

    Unfold sequence.

    Returns a list that contains the elements generated by the given computation. The given initial state argument is passed to the element generator.

    Parameters:

            generator – A function that takes in the current state and returns an option tuple of the next element of the list and the next state value.

            state – The initial state.

    Returns:

        The result list.

zip(other: Iterable[_TResult]) → Iterable[tuple[_TSource, _TResult]]

        Zip sequence.

        Combines the two sequences into a list of pairs. The two sequences need not have equal lengths: when one sequence is exhausted any remaining elements in the other sequence are ignored.

        Parameters:

            other – The second input sequence.
        Returns:

            The result sequence.

append(*others: Iterable[_TSource]) → Callable[[Iterable[_TSource]], Iterable[_TSource]]

    Append sequence to other sequences.

    Wraps the given enumerations as a single concatenated enumeration.

choose(source: Iterable[_TSource], chooser: Callable[[_TSource], Option[_TResult]]) → Iterable[_TResult]

    Choose items from the sequence.

    Applies the given function to each element of the list. Returns the list comprised of the results x for each element where the function returns Some(x).

    Parameters:

            source – The input sequence to to choose from.

            chooser – The function to generate options from the elements.

    Returns:

        The list comprising the values selected from the chooser function.

collect(source: Iterable[_TSource], mapping: Callable[[_TSource], Iterable[_TResult]]) → Iterable[_TResult]

    Collect items from the sequence.

    Applies the given function to each element of the list and concatenates all the resulting sequences. This function is known as bind or flat_map in other languages.

    Parameters:

            source – The input sequence to to collect from.

            mapping – The function to generate sequences from the elements.

    Returns:

        A sequence comprising the concatenated values from the mapping function.

concat(*iterables: Iterable[_TSource]) → Iterable[_TSource]

    Concatenate sequences.

    Combines the given variable number of enumerations and/or enumeration-of-enumerations as a single concatenated enumeration.

    Parameters:

        iterables – The input enumeration-of-enumerations.
    Returns:

        The result sequence.

delay(generator: Callable[[], Iterable[_TSource]]) → Iterable[_TSource]

    Delay sequence.

    Returns a sequence that is built from the given delayed specification of a sequence.

    The input function is evaluated each time an Iterator for the sequence is requested.

    Parameters:

        generator – The generating function for the sequence.

empty: Seq[Any] = []

    The empty sequence.

filter(source: Iterable[_TSource], predicate: Callable[[_TSource], bool]) → Iterable[_TSource]

    Filter sequence.

    Filters the sequence to a new sequence containing only the elements of the sequence for which the given predicate returns True.

    Parameters:

            source – (curried) The input sequence to to filter.

            predicate – A function to test whether each item in the input sequence should be included in the output.

    Returns:

        A partially applied filter function.

fold(source: Iterable[_TSource], folder: Callable[[_TState, _TSource], _TState], state: _TState) → _TState

    Fold elements in sequence.

    Applies a function to each element of the collection, threading an accumulator argument through the computation. If the input function is f and the elements are i0…iN then computes f (… (f s i0)…) iN.

    Parameters:

            source – The input sequence to fold.

            folder – A function that updates the state with each element from the sequence.

            state – The initial state.

    Returns:

        Partially applied fold function that takes a source sequence and returns the state object after the folding function is applied to each element of the sequence.

fold_back(folder: Callable[[_TSource, _TState], _TState], source: Iterable[_TSource]) → Callable[[_TState], _TState]

    Fold elements in sequence backwards.

    Applies a function to each element of the collection, starting from the end, threading an accumulator argument through the computation. If the input function is f and the elements are i0…iN then computes f i0 (… (f iN s)…).

    Parameters:

            folder – A function that updates the state with each element from the sequence.

            source – The input sequence to fold backwards.

    Returns:

        Partially applied fold_back function.

head(source: Iterable[_TSource]) → _TSource

    Return the first element of the sequence.

    Parameters:

        source – The input sequence.
    Returns:

        The first element of the sequence.
    Raises:

        Raises ValueError if the source sequence is empty. –

iter(source: Iterable[_TSource], action: Callable[[_TSource], None]) → None

    Applies the given function to each element of the collection.

    Parameters:

            source – The input sequence to iterate.

            action – A function to apply to each element of the sequence.

    Returns:

        A partially applied iter function.

map(source: Iterable[_TSource], mapper: Callable[[_TSource], _TResult]) → Iterable[_TResult]

    Map source sequence.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection.

    Parameters:

            source – The input sequence to map.

            mapper – A function to transform items from the input sequence.

    Returns:

        Partially applied map function.

mapi(source: Iterable[_TSource], mapping: Callable[[int, _TSource], _TResult]) → Iterable[_TResult]

    Map list with index.

    Builds a new collection whose elements are the results of applying the given function to each of the elements of the collection. The integer index passed to the function indicates the index (from 0) of element being transformed.

    Parameters:

            source – The input sequence to to map.

            mapping – The function to transform elements and their indices.

    Returns:

        The list of transformed elements.

max(source: Iterable[_TSupportsGreaterThan]) → _TSupportsGreaterThan

    Return maximum of all elements.

    Returns the greatest of all elements of the sequence, compared via max().

min(source: Iterable[_TSupportsLessThan]) → _TSupportsLessThan

    Return the minimum of all elements.

    Returns the smallest of all elements of the sequence, compared via max().

of(*args: _TSource) → Seq[_TSource]

    Create sequence from iterable.

    Enables fluent dot chaining on the created sequence object.

of_iterable(source: Iterable[_TSource]) → Seq[_TSource]

    Alias to Seq.of.

of_list(source: Iterable[_TSource]) → Seq[_TSource]

    Alias to seq.of_iterable.

scan(source: Iterable[_TSource], scanner: Callable[[_TState, _TSource], _TState], state: _TState) → Iterable[_TState]

    Scan elements in sequence.

    Like fold, but computes on-demand and returns the sequence of intermediary and final results.

    Parameters:

            source – The input sequence.

            scanner – A function that updates the state with each element

            state – The initial state.

singleton(item: _TSource) → Seq[_TSource]

    Returns a sequence that yields one item only.

    Parameters:

        item – The input item.
    Returns:

        The result sequence of one item.

skip(source: Iterable[_TSource], count: int) → Iterable[_TSource]

    Skip elements from sequence.

    Returns a sequence that skips N elements of the underlying sequence and then yields the remaining elements of the sequence.

    Parameters:

            source – The input sequence.

            count – The number of items to skip.

sum(source: Iterable[_TSupportsSum]) → _TSupportsSum

    Returns the sum of the elements in the sequence.

sum_by(source: Iterable[_TSource], projection: Callable[[_TSource], _TSupportsSum]) → _TSupportsSum

    Sum all elements in sequence.

    Returns the sum of the results generated by applying the function to each element of the sequence.

tail(source: Iterable[_TSource]) → Iterable[_TSource]

    Return tail of sequence.

    Returns a sequence that skips 1 element of the underlying sequence and then yields the remaining elements of the sequence.

take(source: Iterable[_TSource], count: int) → Iterable[_TSource]

    Returns the first N elements of the sequence.

    Parameters:

            source – The source sequence.

            count – The number of items to take.

    Returns:

        The result sequence.

unfold(state: _TState, generator: Callable[[_TState], Option[tuple[_TSource, _TState]]]) → Iterable[_TSource]

    Unfold sequence.

    Generates a list that contains the elements generated by the given computation. The given initial state argument is passed to the element generator.

    Parameters:

            state – The initial state.

            generator – A function that takes in the current state and returns an option tuple of the next element of the list and the next state value.

    Returns:

        A partially applied unfold function that takes the state and returns the result list.

zip(source1: Iterable[_TSource]) → Callable[[Iterable[_TResult]], Iterable[tuple[_TSource, _TResult]]]

    Zip sequence with other.

    Combines the two sequences into a list of pairs. The two sequences need not have equal lengths: when one sequence is exhausted any remaining elements in the other sequence are ignored.

    Parameters:

        source1 – The first input sequence.
    Returns:

        Partially applied zip function.

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
# Callbacks and Continuations

> Don't call me. I'll call you.

```python
import threading

def long_running(callback):
    def done():
        result = 42
        callback(result)
    timer = threading.Timer(5.0, done)
    timer.start()

long_running(print)
```

## Continuation Passing Style (CPS)

This is a functional programming style where you don’t return any values from your
functions. Instead of returning the result, you pass a continuation function that will
be applied to the result.

```python
import math
from expression import Cont

def add(a, b):
    return Cont.Return(a + b)

def square(x):
    return Cont.Return(x * x)

def sqrt(x):
    return Cont.Return(math.sqrt(x))

def pythagoras(a, b):
    return square(a).bind(lambda aa:
           square(b).bind(lambda bb:
           add(aa, bb).bind(lambda aabb:
           sqrt(aabb))))
```

```python
result = pythagoras(2, 3).run()
print(result)
```

## Conclusion

Continuation Passing Style (CPS) can be effectively managed using the `expression` library in Python, leading to cleaner and more maintainable code.
# Data Modelling

Learn how to effectively model data types using Expression in Python with data-classes and tagged-unions.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
from expression import case, tag, tagged_union

# Simple data types using dataclasses
@dataclass
class Rectangle:
    width: float
    length: float

@dataclass
class Circle:
    radius: float

# Tagged union for type safety
@tagged_union
class Shape:
    tag: Literal["rectangle", "circle"] = tag()

    rectangle: Rectangle = case()
    circle: Circle = case()

    @staticmethod
    def Rectangle(width: float, length: float) -> Shape:
        return Shape(rectangle=Rectangle(width, length))

    @staticmethod
    def Circle(radius: float) -> Shape:
        return Shape(circle=Circle(radius))

# Using pattern matching with tagged unions
def calculate_area(shape: Shape) -> float:
    match shape:
        case Shape(tag="rectangle", rectangle=rect):
            return rect.width * rect.length
        case Shape(tag="circle", circle=circ):
            return 3.14 * circ.radius ** 2
        case _:
            raise ValueError("Unknown shape")

# Example usage
rect = Shape.Rectangle(width=10, length=5)
circle = Shape.Circle(radius=3)

print(f"Rectangle area: {calculate_area(rect)}")
print(f"Circle area: {calculate_area(circle)}")
```

This example demonstrates:
1. Creating simple data types with `@dataclass`
2. Defining tagged unions with `@tagged_union`
3. Using pattern matching for type-safe operations
4. Static factory methods for constructing union cases

Tagged unions provide better type safety than regular unions and support nested structures. Each case in a tagged union produces the same type, making them ideal for modeling domain-specific data structures.
# Effects and Expression

This guide focuses on using the `expression` library to handle effects in Python, specifically using Options.

## Effects

Effects are values with a context. The context varies depending on the effect type.  `expression` provides tools to work with these wrapped values safely.

Examples of effects:

*   Option
*   Result
*   ...

## Effects in Expression

`expression` offers a clean way to manage effects, allowing you to work with wrapped values without explicit error checking.

```python
from expression import effect, Option, Some, Nothing


def divide(a: float, divisor: float) -> Option[float]:
    try:
        return Some(a / divisor)
    except ZeroDivisionError:
        return Nothing


@effect.option[float]()
def comp(x: float):
    result: float = yield from divide(42, x)
    result += 32
    return result


comp(42)
```

In this example:

*   `divide` returns an `Option[float]`, representing either a successful division (`Some`) or a division by zero (`Nothing`).
*   The `@effect.option[float]()` decorator transforms `comp` into an effectful computation.
*   `yield from divide(42, x)` unwraps the `Option` returned by `divide`. If `divide` returns `Nothing`, the entire `comp` function short-circuits and returns `Nothing`. If `divide` returns `Some(value)`, `result` is assigned the unwrapped `value`.
*   The rest of the computation proceeds only if the `Option` was a `Some`.

This approach eliminates the need for manual `if/else` checks for `None` or exceptions, leading to more concise and readable code.
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


ys = pipe(xs, map(lambda x: x * 10))Mailbox
class AsyncReplyChannel(fn: Callable[[_Reply], None])

class MailboxProcessor(cancellation_token: CancellationToken | None)

post(msg: _Msg) → None

    Post a message synchronously to the mailbox processor.

    This method is not asynchronous since it’s very fast to execute. It simply adds the message to the message queue of the mailbox processor and returns.

    Parameters:

        msg – Message to post.
    Returns:

        None

post_and_async_reply(build_message: Callable[[AsyncReplyChannel[_Reply]], _Msg]) → Awaitable[_Reply]

    Post with async reply.

    Post a message asynchronously to the mailbox processor and wait for the reply.

    Parameters:

            build_message – A function that takes a reply channel

            send ((AsyncReplyChannel[Reply]) and returns a message to)

            the (to the mailbox processor. The message should contain)

            tuple. (reply channel as e.g a)

    Returns:

        The reply from mailbox processor.

async receive() → _Msg

    Receive message from mailbox.

    Returns:

        An asynchronous computation which will consume the first message in arrival order. No thread is blocked while waiting for further messages. Raises a TimeoutException if the timeout is exceeded.

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
# Functional Programming with Expression

This tutorial will show you how to use the [Expression](https://github.com/dbrattli/Expression) library for functional programming in Python.

## Key Concepts

Functional programming is about programming with functions (expressions) that evaluate to values. The main concepts we'll cover:

- Pure functions - deterministic, side-effect free functions that are easier to test and reason about
- Higher-order functions - functions that take or return other functions
- Pipeline operations - composing functions in a readable way
- Immutability - using immutable data structures

## Using Expression

### Pipeline Operations

Expression provides a `pipe` function for composing operations in a readable way:

```python
from expression import pipe
from expression.collections import seq

xs = seq.range(10)

result = pipe(
        xs,
        seq.map(lambda x: x * 10),
        seq.filter(lambda x: x > 50),
        seq.fold(lambda s, x: s + x, 0),
)
```

### Currying and Partial Application 

The library supports currying functions using the `@curry` decorator:

```python
from expression import curry

@curry(1)
def add(a: int, b: int) -> int:
        return a + b

add(3)(4)  # Returns 7
```

### Collection Operations

Expression provides functional collection operations through the `seq` module:

```python
from expression.collections import seq

xs = seq.of_iterable(range(10))

mapping = seq.map(lambda x: x * 10)
filter = seq.filter(lambda x: x > 30)

result = pipe(xs,
        mapping, 
        filter,
        list,
)
```

## Best Practices

1. Use pure functions whenever possible
2. Leverage Expression's pipeline operations for readability
3. Use static type checking (Pylance in strict mode recommended)
4. Write unit tests for core business logic
5. Prefer immutable data structures
6. Keep functions small and focused
7. Use the `@curry` decorator for functions that will be used in pipelines

## Industrial Strength Code

For production-grade functional code:

- Use simple, well-tested abstractions from Expression
- Avoid mutable state and side effects
- Implement thorough unit testing
- Use static type checking
- Write clear, composable functions
- Keep your code single-threaded where possible to avoid concurrency bugs

The Expression library provides the tools needed to write robust functional code while maintaining Python's readability and simplicity.
# Optional Values

In functional programming, we use the Option (or Maybe) type to handle cases where a value might be missing. The Expression library provides an elegant way to work with optional values through its `option` module.

## Creating Options

Import the necessary components:
```python
from expression import Option, option, Some, Nothing
```

Create optional values:
```python
# Some value
x = Some(42)
print(x)  # Some(42)

# No value
y = Nothing
print(y)  # Nothing
```

## Option-Returning Functions

Create safe functions that return options:
```python
def keep_positive(a: int) -> Option[int]:
    return Some(a) if a > 0 else Nothing

def divide(a: float, divisor: float) -> Option[float]:
    try:
        return Some(a/divisor)
    except ZeroDivisionError:
        return Nothing
```

## Transforming Options

Transform options without explicit null checking using `pipe` and `option.map`:
```python
from expression import pipe

result = pipe(
    Some(42),
    option.map(lambda x: x * 10)
)
print(result)  # Some(420)

# Nothing values propagate through transformations
result = pipe(
    Nothing,
    option.map(lambda x: x * 10)
)
print(result)  # Nothing
```

## Option Effects

Use the `@effect.option` decorator for railway-oriented programming:
```python
from expression import effect

@effect.option[int]()
def calculate():
    x = yield 42
    y = yield from Some(43)
    return x + y

result = calculate()
print(result)  # Some(85)

@effect.option[int]()
def failing_calculation():
    x = yield from Nothing
    # Following code won't execute
    y = yield from Some(43)
    return x + y

result = failing_calculation()
print(result)  # Nothing
```

For more information, check the [API reference](https://expression.readthedocs.io/en/latest/reference/option.html).
# Railway Oriented Programming (ROP)

Railway Oriented Programming (ROP) is a functional error handling technique that uses types to model errors instead of exceptions. This approach can lead to more robust and easier-to-maintain code. The `expression` library provides a `Result` type that facilitates ROP in Python.

## Result in Expression

The `Result[T, TError]` type in `expression` allows you to write composable, error-tolerant code. A `Result` is similar to `Option`, but it lets you define the type of error, such as an exception. This is useful when you need to know why an operation failed.  It serves the same purpose as an `Either` type, where `Left` represents the error and `Right` the success value.

```python
from expression import Ok, Error

def fetch(url):
    try:
        if not "http://" in url:
            raise Exception("Error: unable to fetch from: '%s'" % url)

        value = url.replace("http://", "")
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```python
result = fetch("http://42")
print(result)
```

```python
def parse(string):
    try:
        value = float(string)
        return Ok(value)
    except Exception as exn:
        return Error(exn)
```

```python
result = parse("42")
print(result)
```

## Composition with Pipeline

The `expression` library provides a `pipeline` function for composing functions that return `Result` types. This is also known as "Kleisli composition."

```python
from expression.extra.result import pipeline

def fetch_with_value(x):
    return fetch("http://%s" % x)

request = pipeline(
    fetch,
    fetch_with_value,
    fetch_with_value,
    parse
)

result = request("http://123")
print(result)
```

## Effect notation

```python
from expression import effect, Ok, Result

@effect.result[int, Exception]()
def fn():
    x = yield from Ok(42)
    y = yield from Ok(10)
    return x + y

xs = fn()
assert isinstance(xs, Result)
```

A simplified type called [`Try`](reference_try) is also available. It's a result type
that is pinned to `Exception` i.e., `Result[TSource, Exception]`. This makes the code
simpler since you don't have specify the error type every time you declare the type of
your result.
