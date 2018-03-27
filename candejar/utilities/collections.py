# -*- coding: utf-8 -*-

"""Special collections types."""

import collections
from collections.abc import MutableSequence
from typing import List, Tuple, Any


class ChainSequence(MutableSequence):
    """Combines multiple sequences together. Similar to `collections.ChainMap`"""
    sequences: MutableSequence

    def __init__(self, *sequences):
        self.sequences = sequences

    def __delitem__(self, idx: int) -> None:
        seq, new_idx = self.get_seq_and_idx(idx)
        del seq[new_idx]

    def __getitem__(self, idx: int) -> Any:
        seq, new_idx = self.get_seq_and_idx(idx)
        return seq[new_idx]

    def __setitem__(self, idx: int, value: Any) -> None:
        seq, new_idx = self.get_seq_and_idx(idx)
        seq[new_idx] = value

    def __len__(self) -> int:
        return sum(len(s) for s in self.sequences)

    def insert(self, idx: int, value: Any) -> None:
        seq, new_idx = self.get_seq_and_idx(idx)
        seq.insert(new_idx, value)

    def get_seq_and_idx(self, idx: int) -> Tuple[MutableSequence, int]:
        if idx>=len(self) or idx<-len(self):
            raise IndexError(f"{idx!r}")
        if idx<0:
            idx = len(self)+idx
        sequences = iter(self.sequences)
        old_idx = idx
        for s in sequences:
            new_idx = old_idx-len(s)
            if new_idx<0:
                break
            old_idx = new_idx
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
