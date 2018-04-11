# -*- coding: utf-8 -*-

"""Special collections types."""

import collections
from collections.abc import MutableSequence
from typing import List, Tuple, Any


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


    def get_seq_and_idx(self, idx: int) -> Tuple[MutableSequence, int]:
        if -len(self)<idx<0:
            idx = len(self)+idx
        if idx>=len(self):
            cum_len = 0
            for seq,length in zip(self.sequences, self.cumulative_lens):
                if length==len(self):
                    return seq, idx-cum_len
                cum_len = length
        sequences = iter(self.sequences)
        old_idx = idx
        for s in sequences:
            new_idx = old_idx-len(s)
            if new_idx<0:
                break
            old_idx = new_idx
        else:
            old_idx = len(s)
        return s, old_idx

    @property
    def cumulative_lens(self) -> List[int]:
        f_lens = lambda i_last: sum(len(sq) for sq in self.sequences[:i_last + 1])
        return [f_lens(i_last) for i_last in range(len(self.sequences))]

    def new_child(self, s: MutableSequence) -> "ChainSequence":
        return ChainSequence(*self.sequences, s)

    @property
    def parents(self) -> "ChainSequence":
        return ChainSequence(*self.sequences[:-1])


class MyCounter(collections.Counter):
    """A special `collections.Counter` that can be incremented."""
    def incremented(self, key):
        """The post-incremented count of `key`."""
        self[key] += 1
        return self[key]
