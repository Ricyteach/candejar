# -*- coding: utf-8 -*-

"""Special tools for working with candeobj types."""

from __future__ import annotations
from typing import MutableMapping, Iterator, Union, TypeVar, Any, Dict, Callable
import itertools

from . import exc
from .candeseq import Nodes, Elements, NodesSection, ElementsSection

CandeSeq = TypeVar("CandeSeq", bound=Union[Nodes, Elements])
SectionSeq = TypeVar("SectionSeq", bound=Union[NodesSection, ElementsSection])


class SubConverter(MutableMapping[int, int]):
    """Builds a mapping that turns an old item num attribute into a new one
    based on the order. The new new item num attributed begins at the starting
    point, start.
    """

    def __init__(self, start: int, seq: SectionSeq) -> None:
        self.start = start
        self.seq = seq

        seen = set()
        keys = [(num, seen.add(num))[0] for num in self.nums if num not in seen]
        self._d: Dict[int, int] = dict(zip(keys, itertools.count(self.start)))

    def __getitem__(self, k: int) -> int:
        try:
            return self._d.__getitem__(k)
        except KeyError:
            if k in self.nums:
                raise exc.CandeKeyError(f"conversion value missing for item num {k!s}")
            raise exc.CandeKeyError(f"item num {k!s} does not appear in {type(self.seq).__qualname__}")

    def __setitem__(self, k: int, v: int) -> None:
        if k not in self._d.keys() and k not in self.nums:
            raise exc.CandeKeyError(f"can only change existing keys - {k!s} not in nums;")
        else:
            self._d.__setitem__(k, v)

    def __delitem__(self, k: int) -> None:
        self._d.__delitem__(k)

    def __iter__(self) -> Iterator[int]:
        return iter(self._d)

    def __len__(self) -> int:
        return self._d.__len__()

    def __repr__(self) -> str:
        return f'SubConverter(start={self.start!r}, {self._d!r})'

    @property
    def nums(self) -> Iterator[int]:
        """The current num attributes for the referenced section sequence"""
        yield from (i.num for i in self.seq)

    def copy(self) -> SubConverter:
        cls = type(self)
        o = cls.__new__(cls)
        o.start, o.seq, o._d = self.start, self.seq, self._d.copy()
        return o

class NumConverter(MutableMapping[int, SubConverter]):
    """Builds a mapping of SubConverter objects assigned to each section"""

    def __init__(self, seq: CandeSeq):
        self.seq = seq
        self._d: Dict[int, SubConverter] = dict()

        start = 1
        for section_seq in self.seq.seq_map.values():
            c = self._d[id(section_seq)] = SubConverter(start, section_seq)
            start += len(c)

    def __getitem__(self, k: int) -> SubConverter:
        try:
            return self._d.__getitem__(k)
        except KeyError:
            if k in self.ids:
                raise exc.CandeKeyError(f"conversion mapping missing for section name {k!s}")
            raise exc.CandeKeyError(f"section name {k!s} does not appear in {type(self.seq).__qualname__}")

    def __setitem__(self, k: int, v: SubConverter) -> None:
        if k not in self._d.keys() and k not in self.ids:
            raise exc.CandeKeyError(f"can only change existing keys - {k!s} not in sections;")
        else:
            self._d.__setitem__(k, v)

    def __delitem__(self, k: int) -> None:
        if k in self.ids:
            raise exc.CandeKeyError(f"section name {k!s} must first be removed from {type(self.seq).__qualname__}")
        self._d.__delitem__(k)

    def __iter__(self) -> Iterator[int]:
        return self._d.__iter__()

    def __len__(self) -> int:
        return self._d.__len__()

    def __repr__(self) -> str:
        return f'NumConverter(seq_type={self.seq_type!r}, seq_len={self.seq_len!r}, seq_id={self.seq_id!r})'

    def by_name(self, name: str):
        return self._d[id(self.seq[name])]

    def renumber(self):
        """Reset the global new_num values of exising converter taking into account repeated node numbers"""
        count = 1
        renumbered_lookup = dict()
        for sub_converter in self.values():
            for old_num, new_num in sub_converter.items():
                if new_num not in renumbered_lookup.keys():
                    sub_converter[old_num] = count
                    renumbered_lookup[new_num] = count
                    count += 1
                sub_converter[old_num] = renumbered_lookup[new_num]

    @property
    def seq_id(self) -> int:
        return id(self.seq)

    @property
    def seq_len(self) -> int:
        return len(self.seq)

    @property
    def seq_type(self) -> str:
        return type(self.seq).__qualname__

    @property
    def ids(self) -> Iterator[Any]:
        """The current section names for the referenced CANDE item sequence"""
        yield from (id(v) for v in self.seq.seq_map.values())
