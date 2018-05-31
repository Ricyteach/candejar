# -*- coding: utf-8 -*-

"""Special collections types."""

from __future__ import annotations
import collections
import itertools
from collections.abc import MutableSequence
from typing import List, Tuple, Any, overload


class ChainSequence(MutableSequence):
    """Combines multiple sequences together. Similar to `collections.ChainMap`

    All operations default to the left-most subsequence except for `append`, which defaults to the right-most.
    """
    sequences: MutableSequence

    def __init__(self, *sequences):
        self.sequences = sequences if sequences else [[]]

    def __delitem__(self, idx: int) -> None:
        seq, new_idx = self.get_seq_and_idx(idx)
        try:
            del seq[new_idx]
        except IndexError:
            raise IndexError(f"{idx!s}") from None

    def __getitem__(self, idx: int) -> Any:
        seq, new_idx = self.get_seq_and_idx(idx)
        try:
            return seq[new_idx]
        except IndexError:
            raise IndexError(f"{idx!s}") from None

    def __setitem__(self, idx: int, value: Any) -> None:
        seq, new_idx = self.get_seq_and_idx(idx)
        try:
            seq[new_idx] = value
        except IndexError:
            raise IndexError(f"{idx!s}") from None

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
    def get_seq_and_idx(self, i: int) -> Tuple[MutableSequence, int]: ...

    @overload
    def get_seq_and_idx(self, s: slice) -> List[Tuple[MutableSequence, int]]: ...

    def get_seq_and_idx(self, x):
        x_list=range(len(self))[x]
        if isinstance(x_list, int):
            x_list = [x_list]
        else:
            x_list = list(x_list)
        seqidx_idx_list=[]
        lengths = self.cumulative_lens
        for idx in x_list:
            offsets = [idx-l for l in lengths]
            seqidx = next((seqidx, idx) for seqidx, offset in enumerate(offsets) if offset > 0)
            seqidx_idx_list.append()

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

    def new_child(self, s: MutableSequence) -> ChainSequence:
        return ChainSequence(*self.sequences, s)

    @property
    def parents(self) -> ChainSequence:
        return ChainSequence(*self.sequences[:-1])
