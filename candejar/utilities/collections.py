# -*- coding: utf-8 -*-

"""Special collections types."""

from __future__ import annotations
import itertools
from typing import List, Tuple, Any, overload, Sequence, MutableSequence, Generic, TypeVar, Type, Union, Optional, \
    Iterable, Iterator, Mapping, Callable, ClassVar

T = TypeVar("T")
NO_SLICE = object()


class SpecialValueError(ValueError):
    pass


def cleanup_falsey(sequences):
    """Removes falsey items (e.g. empty sub sequences) from the sequences argument"""
    if not all(sequences):
        for i in range(len(sequences), -1, -1):
            if not sequences[i]:
                del sequences[i]
    if not sequences:
        sequences.append([])


class ManagedChain(Generic[T]):
    """A mutable sequence descriptor that cannot be deleted, and always has at least one mutable sub sequence"""

    def __get__(self, instance: Optional[ChainSequence[T]], owner: Type[ChainSequence[T]]) -> Union[
        ManagedChain[T], MutableSequence[T]]:
        if instance is not None:
            return instance._sequences
        else:
            return self

    def __set__(self, instance: ChainSequence, value: T) -> None:
        if not isinstance(value, MutableSequence):
            raise TypeError(f"the ManagedChain requires a mutable sequence object")
        if not value:
            value.append([])
        instance._sequences = value

    def __delete__(self, instance: ChainSequence) -> None:
        raise AttributeError(f"deletion of the ManagedChain is not allowed")


class ChainSequence(MutableSequence[T]):
    """Combines multiple sequences together. Similar to `collections.ChainMap`.

    Operations default to the left-most subsequence except for `append`, which defaults to the right-most.
    """
    sequences: ManagedChain[T] = ManagedChain()

    def __init__(self, *sequences: Sequence[Sequence[T]]) -> None:
        self.sequences = list(sequences) if sequences else [[]]

    def __repr__(self):
        return "[{}]".format(", ".join(f"{s!r}" for s in self.sequences))

    @overload
    def __delitem__(self, i: int) -> None:
        ...

    @overload
    def __delitem__(self, s: slice) -> None:
        ...

    def __delitem__(self, x):
        seq, new_idx = self.get_seq_and_idx(x)
        try:
            del seq[new_idx]
        except IndexError as e:
            raise IndexError(f"{x!s}") from e

    @overload
    def __getitem__(self, i: int) -> T:
        ...

    @overload
    def __getitem__(self, s: slice) -> Sequence[T]:
        ...

    def __getitem__(self, x):
        seq, new_idx = self.get_seq_and_idx(x)
        try:
            return seq[new_idx]
        except IndexError:
            raise IndexError(f"{x!s}") from None

    @overload
    def __setitem__(self, i: int, value: T) -> None:
        ...

    @overload
    def __setitem__(self, s: slice, value: Iterable[T]) -> None:
        ...

    def __setitem__(self, x: int, value) -> None:
        try:
            seq, new_idx = self.get_seq_and_idx(x)
        except SpecialValueError as e:
            is_slice = isinstance(x, slice)
            raise NotImplementedError(
                "setting by slice is not supported") if is_slice else e from e if is_slice else None
        try:
            seq[new_idx] = value
        except IndexError:
            raise IndexError(f"{x!s}") from None

    def __len__(self) -> int:
        return sum(len(s) for s in self.sequences)

    def insert(self, idx: int, value: Any) -> None:
        seq, new_idx = self.get_seq_and_idx(idx)
        seq.insert(new_idx, value)

    def append(self, item: Any, map_idx: int = -1):
        """Appending defaults to the last subsequence."""
        try:
            s = self.sequences[map_idx]
        except IndexError:
            raise IndexError(f"Invalid map index [{map_idx:d}] provided for "
                             f"{len(self.sequences):d} sequences") from None
        else:
            s.append(item)

    @overload
    def iter_seqidx_and_slice_or_idx(self, i: int) -> Iterator[Optional[int]]:
        ...

    @overload
    def iter_seqidx_and_slice_or_idx(self, s: slice) -> Iterator[Optional[slice]]:
        ...

    def iter_seqidx_and_slice_or_idx(self, x):
        if isinstance(x, int):
            yield from self._iter_seqidx_and_idx(x)
        elif isinstance(x, slice):
            yield from self._iter_seqidx_and_slice(x)
        else:
            raise TypeError(f"{type(self).__qualname__} indices must be integers or slices, not {type(x).__qualname__}")

    def _iter_seqidx_and_idx(self, i: int) -> Iterator[Optional[int]]:
        """Places a positive index in the context of the sub-sequences

        None means that the supplied index doesn't apply to the associated sub-sequence
        """
        if i < 0:
            raise SpecialValueError("i must be zero or greater")
        sequences_len = len(self.sequences)
        if sequences_len == 0:
            return
        else:
            indexes: List[Optional[int]] = []
            prev_cumlen = 0
            for seq, sub_seq_cumlen in zip(self.sequences, self.cumulative_lens):
                diff = i - sub_seq_cumlen
                if not seq:
                    indexes.append(None)
                elif diff < 0:
                    indexes.append(i - prev_cumlen if all(y is None for y in indexes) else None)
                else:
                    indexes.append(None)
                yield indexes[-1]
                prev_cumlen = sub_seq_cumlen

    def _iter_seqidx_and_slice(self, s: slice) -> Iterator[Optional[slice]]:
        # TODO: implement slicing steps other than 1
        sequences_len = len(self.sequences)
        if s == slice(None):
            yield from (s for _ in range(sequences_len))
            return
        if s.step == 0:
            raise ValueError("slice step cannot be zero")
        if s.step and slice.step != 1:
            raise NotImplementedError("slice steps other than 1 not  yet implemented")
        chain_len = len(self)
        slice_range = range(chain_len)[s]
        if not slice_range:
            yield from (None for _ in range(sequences_len))
            return
        s_starts = list(self._iter_seqidx_and_idx(slice_range.start))
        s_stops = list(self._iter_seqidx_and_idx(slice_range.stop))
        starts_seen, stops_seen = [], []
        yielded = []
        if (s.step if s.step is not None else 0) < 0:
            s_starts, s_stops = s_stops, s_starts
        for sdx, (start_dx, stop_dx, cum_len) in enumerate(zip(s_starts, s_stops, self.cumulative_lens)):
            start: Optional[Union[type(NO_SLICE), int]]
            if s.start is None and (s.step is None or s.step == 1):
                start = None
            elif start_dx is None:
                if all(s is None for s in starts_seen):
                    start = NO_SLICE
                else:
                    start = None
            else:
                start = start_dx
            stop: Optional[Union[type(NO_SLICE), int]]
            if s.stop is None and (s.step is None or s.step == 1):
                stop = None
            elif stop_dx is None:
                if all(s is None for s in stops_seen):
                    stop = None
                else:
                    stop = NO_SLICE
            else:
                stop = stop_dx
            if NO_SLICE in (start, stop):
                yielded.append(None)
            else:
                yielded.append(slice(start, stop, s.step))
            yield yielded[-1]
            starts_seen.append(start_dx)
            stops_seen.append(stop_dx)

    @overload
    def get_seq_and_idx(self, i: int) -> Tuple[MutableSequence, int]:
        ...

    @overload
    def get_seq_and_idx(self, s: slice) -> List[Tuple[MutableSequence, int]]:
        ...

    def get_seq_and_idx(self, x):
        x_list = range(len(self))[x]
        if isinstance(x_list, int):
            x_list = [x_list]
        else:
            x_list = list(x_list)
        seq_idx_list = []
        for idx in x_list:
            sequences = iter(self.sequences)
            old_idx = idx
            for s in sequences:
                new_idx = old_idx - len(s)
                if new_idx < 0:
                    break
                old_idx = new_idx
            else:
                old_idx = len(s)
            seq_idx_list.append((s, old_idx))
        if len(seq_idx_list) == 1:
            return seq_idx_list[0]
        else:
            return seq_idx_list

    @property
    def cumulative_lens(self) -> List[int]:
        return list(itertools.accumulate(len(s) for s in self.sequences))

    def new_child(self, s: Sequence = None) -> ChainSequence:
        return ChainSequence(*self.sequences, s)

    @property
    def parents(self) -> ChainSequence:
        return ChainSequence(*self.sequences[:-1])


V = TypeVar("V")


class KeyedChainView(MutableSequence[V]):
    """A mutable viewer of underlying sub-sequences, each with a key.

    The sequence related methods act on the underlying sub-sequences. Other
    methods act on the mapping. Some (getitem, setitem, and delitem) do both
    dependong on the index/key value given.

    The key(s) associated with the underlying sub-sequences can be any hashable
    value, but not int (to allow indexing of the sub-sequences).
    """
    __slots__ = ("seq_map")

    def __init__(self, seq_map: Optional[Mapping[Any, Sequence[V]]] = None, **kwargs: Iterable[V]) -> None:
        if seq_map and any(isinstance(k,int) for k in seq_map.keys()):
            raise TypeError("int keys are not allowed for seq_map")
        if seq_map is None:
            seq_map = {}
        seq_map.update({k: (v if isinstance(v, Sequence) else list(v)) for k, v in kwargs.items()})
        self.seq_map = seq_map

    def __repr__(self) -> str:
        return f"KeyedChainView({self.seq_map!r})"

    def __contains__(self, item) -> bool:
        return item in set(v for s in self.seq_map.values() for v in s)

    def __iter__(self) -> Iterator[V]:
        yield from (v for seq in self.seq_map.values() for v in seq)

    def __reversed__(self) -> Iterator[V]:
        yield from (v for seq in reversed(self.seq_map.values()) for v in reversed(seq))

    def reverse(self):
        self.seq_map = type(self.seq_map)(reversed(self.seq_map.items()))
        for seq in self.seq_map.values():
            seq.reverse()

    def __len__(self) -> int:
        return sum(len(s) for s in self.seq_map.values()) if self.seq_map else 0

    def get_seq_idx(self, i: int) -> Tuple[Sequence[V], int]:
        """Convert an index to a sub-sequence index"""
        chain_len = len(self)
        try:
            idx = range(chain_len)[i]
        except IndexError:
            raise IndexError(f"{type(self).__qualname__} index out of range") from None
        ctr = itertools.count()
        for s in self.seq_map.values():
            for i_, ct in zip(range(len(s)), ctr):
                if ct == idx:
                    return s, i_

    def iter_seq_slice(self, s: slice) -> Iterator[Tuple[Sequence[V], slice]]:
        raise NotImplementedError()

    @overload
    def __getitem__(self, i: int) -> V:
        ...

    @overload
    def __getitem__(self, s: slice) -> List[V]:
        ...

    @overload
    def __getitem__(self, k: Any) -> Sequence[V]:
        ...

    def __getitem__(self, x):
        if isinstance(x, slice):
            iter_s_x_del = self.iter_seq_slice(x)
            return [s[x_get] for s, x_get in iter_s_x_del]
        else:
            if isinstance(x, int):
                s, x_get = self.get_seq_idx(x)
            else:
                s, x_get = self.seq_map, x
            return s[x_get]

    @overload
    def __setitem__(self, i: int, v: V) -> None:
        ...

    @overload
    def __setitem__(self, s: slice, v: Iterable[V]) -> None:
        ...

    @overload
    def __setitem__(self, k: Any, v: Sequence[V]) -> None:
        ...

    def __setitem__(self, x, v):
        if isinstance(x, slice):
            raise TypeError(f"{type(self).__qualname__} slice assignment not supported")
        else:
            if isinstance(x, int):
                s, x_set = self.get_seq_idx(x)
            else:
                s, x_set = self.seq_map, x
            s[x_set] = v

    @overload
    def __delitem__(self, i: int) -> None:
        ...

    @overload
    def __delitem__(self, s: slice) -> None:
        ...

    @overload
    def __delitem__(self, k: Any) -> None:
        ...

    def __delitem__(self, x):
        if isinstance(x, slice):
            iter_s_x_del = self.iter_seq_slice(x)
            for s, x_del in iter_s_x_del:
                del s[x_del]
        else:
            if isinstance(x, int):
                s, x_del = self.get_seq_idx(x)
            else:
                s, x_del = self.seq_map, x
            del s[x_del]

    def append(self, v: V) -> None:
        try:
            s = list(self.seq_map.values())[-1]
        except IndexError:
            raise IndexError(f"cannot append to an empty {type(self).__qualname__}") from None
        else:
            s.append(v)

    def extend(self, iterable: Iterable[V]):
        try:
            s = list(self.seq_map.keys())[-1]
        except IndexError:
            raise IndexError(f"cannot extend an empty {type(self).__qualname__}") from None
        else:
            s.extend(iterable)

    # TODO: pop dict key
    def pop(self, index: int = ...) -> V:
        try:
            s, i = self.get_seq_idx(index)
        except TypeError:
            for s in reversed(self.seq_map.values()):
                try:
                    return s.pop()
                except IndexError:
                    continue
            else:
                raise IndexError(f"cannot pop from empty {type(self).__qualname__}")
        except IndexError:
            raise IndexError("pop index out of range") from None
        else:
            return s.pop(i)

    def insert(self, index: int, object: V) -> None:
        try:
            s, i = self.get_seq_idx(index)
        except IndexError as e:
            if index == 0:
                raise e
            else:
                pass
        else:
            s.insert(i, object)
            return
        s_list = list(self.seq_map.values())
        try:
            if index < 0:
                s_list[0].insert(0, object)
            else:
                s_list[-1].append(object)
        except IndexError:
            raise IndexError(f"cannot insert to empty {type(self).__qualname__}")

    def remove(self, object: V):
        for idx, v in enumerate(iter(self)):
            if object == v:
                s, i = self.get_seq_idx(idx)
                break
        else:
            t_name = type(self).__qualname__
            raise ValueError(f"{t_name}.remove(x): x not in {t_name}")
        del s[i]

    def index(self, object: V, start: int = ..., stop: int = ...):
        try:
            r = range(start, stop)
        except TypeError as e:
            if ... in (start, stop):
                if start == ...:
                    start = 0
                if stop == ...:
                    stop = len(self)
                self.index(object, start, stop)
                return
            else:
                raise e
        value_error = ValueError(f"{object!s} is not in {type(self).__qualname__}")
        if not r:
            raise value_error
        for idx, v in enumerate(iter(self)):
            if object == v:
                _, i = self.get_seq_idx(idx)
                return i
        else:
            raise value_error

    def count(self, object: V):
        return sum(v for v in iter(self) if v==object)

    def popitem(self, last: bool = True) -> Tuple[Any, Sequence[V]]:
        idx = {True: -1, False: 0}[bool(last)]
        try:
            k = list(self.seq_map.keys())[idx]
        except IndexError:
            raise KeyError(f"{type(self).__qualname__} is empty")
        else:
            return k, self.seq_map.pop(k)

    # TODO: fix to use key argument
    def move_to_end(self, key: Any, last:bool=True) -> None:
        idx = {True: -1, False: 0}[bool(last)]
        try:
            k = list(self.seq_map.keys())[idx]
        except IndexError:
            raise KeyError(f"{type(self).__qualname__} is empty")
        else:
            v = self.seq_map.pop(k)
        copy = self.seq_map.copy()
        self.seq_map.clear()
        if idx==0:
            self.seq_map.update({k:v})
            self.seq_map.update(copy)
        else:
            self.seq_map.update(copy)
            self.seq_map.update({k:v})

    def __eq__(self, other: Mapping) -> bool:
        try:
            o_keys = other.keys()
        except AttributeError:
            pass
        else:
            if set(self.seq_map.keys()) == set(o_keys):
                for k in self.seq_map.keys():
                    result = self.seq_map[k] == other[k]
                    if not result:
                        break
                else:
                    return True
        return False

    def __ne__(self, other: Mapping) -> bool:
        return not self.__eq__(other)

    def __iadd__(self, other: Any) -> KeyedChainView:
        raise TypeError(f"{type(self).__qualname__} addition operation not supported")

    def __add__(self, other: Any) -> KeyedChainView:
        raise TypeError(f"{type(self).__qualname__} addition operation not supported")


class CollectionConvertingMixin(Generic[T]):
    __slots__ = ()

    converter: ClassVar[Callable[[Any], T]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        try:
            cls.converter = staticmethod(kwargs.pop("kwarg_convert"))
        except KeyError:
            pass
        super().__init_subclass__(**kwargs)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        try:
            converter_is_cls = isinstance(self.converter, type)
        except AttributeError:
            raise TypeError(f"cannot instantiate {type(self).__qualname__} without 'converter' class attribute")
        for i, v in enumerate(iter(self)):
            if not converter_is_cls or (converter_is_cls and not isinstance(v, self.converter)):
                self[i] = self.converter(v)
