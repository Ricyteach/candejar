# -*- coding: utf-8 -*-

"""Special collections types."""

from __future__ import annotations
import itertools
from typing import List, Tuple, Any, overload, Sequence, MutableSequence, Generic, TypeVar, Type, Union, Optional, \
    Iterable, Iterator

T=TypeVar("T")

def cleanup_falsey(sequences):
    """Removes falsey items (e.g. empty sub sequences) from the sequences argument"""
    if not all(sequences):
        for i in range(len(sequences),-1,-1):
            if not sequences[i]:
                del sequences[i]
    if not sequences:
        sequences.append([])

class ManagedChain(Generic[T]):
    """A mutable sequence descriptor that cannot be deleted, and always has at least one mutable sub sequence"""
    def __get__(self, instance:Optional[ChainSequence[T]], owner:Type[ChainSequence[T]]) -> Union[ManagedChain[T], MutableSequence[T]]:
        if instance is not None:
            return instance._sequences
        else:
            return self

    def __set__(self, instance: ChainSequence, value: T) -> None:
        if not isinstance(value,MutableSequence):
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

    @overload
    def __delitem__(self, i: int) -> None:...

    @overload
    def __delitem__(self, s: slice) -> None:...

    def __delitem__(self, x):
        seq, new_idx = self.get_seq_and_idx(x)
        try:
            del seq[new_idx]
        except IndexError as e:
            raise IndexError(f"{x!s}") from e

    @overload
    def __getitem__(self, i: int) -> T:...

    @overload
    def __getitem__(self, s: slice) -> Sequence[T]:...

    def __getitem__(self, x):
        seq, new_idx = self.get_seq_and_idx(x)
        try:
            return seq[new_idx]
        except IndexError:
            raise IndexError(f"{x!s}") from None

    @overload
    def __setitem__(self, i: int, value: T) -> None:...

    @overload
    def __setitem__(self, s: slice, value: Iterable[T]) -> None:...

    def __setitem__(self, x: int, value) -> None:
        seq, new_idx = self.get_seq_and_idx(x)
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
    def iter_seqidx_and_slice_or_idx(self, i: int) -> Iterator[Optional[int]]: ...

    @overload
    def iter_seqidx_and_slice_or_idx(self, s: slice) -> Iterator[Optional[slice]]: ...

    def iter_seqidx_and_slice_or_idx(self, x):
        if isinstance(x,int):
            yield from self._iter_seqidx_and_idx(x)
        elif isinstance(x,slice):
            yield from self._iter_seqidx_and_slice(x)
        else:
            raise TypeError(f"{type(self).__qualname__} indices must be integers or slices, not {type(x).__qualname__}")

    def _iter_seqidx_and_idx(self, i: int) -> Iterator[Optional[int]]:
        """Places a positive index in the context of the sub-sequences

        None means that the supplied index doesn't apply to the associated sub-sequence"""
        if i<0:
            raise ValueError("i must be zero or greater")
        sequences_len = len(self.sequences)
        if sequences_len==0:
            yield i
        else:
            indexes: List[Optional[int]]=[]
            for seq,sub_seq_cumlen in zip(self.sequences, self.cumulative_lens):
                idx = i-sub_seq_cumlen
                if not seq:
                    indexes.append(None)
                elif idx<0:
                    indexes.append(i if all(y is None for y in indexes) else None)
                else:
                    indexes.append(idx)
                yield indexes[-1]

    def _iter_seqidx_and_slice(self, s: slice) -> Iterator[Optional[slice]]:
        if slice.step==0:
            raise ValueError("slice step cannot be zero")
        sequences_len = len(self.sequences)
        s_range = range(sequences_len)[s]
        if not s_range:
            yield from (None for _ in range(sequences_len))
            return
        s_starts = list(self._iter_seqidx_and_idx(s_range.start))
        if all(start is None for start in s_starts):
            yield from (None for _ in range(sequences_len))
            return
        sdx_start,idx_start = next((sx,ix) for sx,ix in enumerate(s_starts) if ix is not None)
        s_stops = list(self._iter_seqidx_and_idx(s_range.stop))

    @overload
    def get_seq_and_idx(self, i: int) -> Tuple[MutableSequence, int]: ...

    @overload
    def get_seq_and_idx(self, s: slice) -> List[Tuple[MutableSequence, int]]: ...

    def get_seq_and_idx(self, x):
        x_list=range(len(self))[x]
        if isinstance(x_list, int):
            x_list = [x_list]
        else:
            x_list = list(x_list)
        seq_idx_list=[]
        for idx in x_list:
            sequences = iter(self.sequences)
            old_idx = idx
            for s in sequences:
                new_idx = old_idx-len(s)
                if new_idx<0:
                    break
                old_idx = new_idx
            else:
                old_idx = len(s)
            seq_idx_list.append((s, old_idx))
        if len(seq_idx_list)==1:
            return seq_idx_list[0]
        else:
            return seq_idx_list

    @property
    def cumulative_lens(self) -> List[int]:
        return list(itertools.accumulate(len(s) for s in self.sequences))

    def new_child(self, s: Sequence=None) -> ChainSequence:
        return ChainSequence(*self.sequences, s)

    @property
    def parents(self) -> ChainSequence:
        return ChainSequence(*self.sequences[:-1])
