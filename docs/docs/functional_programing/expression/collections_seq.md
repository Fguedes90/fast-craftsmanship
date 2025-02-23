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

