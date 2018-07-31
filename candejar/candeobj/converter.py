# -*- coding: utf-8 -*-

"""Special tools for working with candeobj types."""

from __future__ import annotations
from typing import MutableMapping, Iterator, Union, TypeVar, Any, Dict, Generic
import itertools

from . import exc
from .parts import Node, Element, Material
from .candeseqbase import CandeSection, CandeMapSequence
from ..utilities.skip import skippable_len, iter_skippable

HasNum = TypeVar("HasNum", bound=Union[Node, Element, Material])


class NumMap(Generic[HasNum], MutableMapping[int, HasNum]):
    """Maps item num attribute values to Cande sequence member objects."""

    def __init__(self, section: CandeSection[HasNum]) -> None:
        self.section = section
        self._d: Dict[int, HasNum] = dict((has_n.num, has_n) for has_n in
                                          iter_skippable(self.section))

    def __getitem__(self, k: int) -> HasNum:
        try:
            return self._d[k]
        except KeyError:
            raise exc.CandeKeyError(f"item num {k!s} does not appear in "
                                    f"{type(self.section).__qualname__}")

    def __setitem__(self, k: int, v: HasNum) -> None:
        if k not in self._d.keys():
            raise exc.CandeKeyError(f"can only change existing keys - "
                                    f"use update() instead")
        else:
            self._d[k] = v

    def __delitem__(self, k: int) -> None:
        del self._d[k]

    def __iter__(self) -> Iterator[int]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def __repr__(self) -> str:
        return f'{type(self).__qualname__!s}({self._d!r})'

    def copy(self) -> NumMap[HasNum]:
        cls = type(self)
        o = cls.__new__(cls)
        o.section, o._d = self.section, self._d.copy()
        return o

    def renumber(self, start: int):
        """Mutates the num attribute values based on the target node order.

        The first num attribute is determined by start argument. Each old item
        num attribute then maps to a node with a new num attribute value. The
        new item num attribute begins at the starting point, start.
        """
        ctr = itertools.count(start)
        for has_num in self.values():
            has_num.num = next(ctr)


class NumMapsManager(Generic[HasNum], MutableMapping[int, NumMap[HasNum]]):
    """Builds a mapping of NumMap objects assigned to each section"""

    def __init__(self, seq: CandeMapSequence[HasNum]):
        self.seq = seq
        self._d: Dict[int, NumMap[HasNum]] = dict()

        section_seq: CandeSection[HasNum]
        for section_seq in self.seq.seq_map.values():
            self._d[id(section_seq)] = NumMap[HasNum](section_seq)

    def __getitem__(self, k: int) -> NumMap[HasNum]:
        try:
            return self._d.__getitem__(k)
        except KeyError:
            if k in self.ids:
                raise exc.CandeKeyError(f"conversion mapping missing for "
                                        f"section name {k!s}")
            raise exc.CandeKeyError(f"section name {k!s} does not appear in "
                                    f"{type(self.seq).__qualname__}")

    def __setitem__(self, k: int, v: NumMap[HasNum]) -> None:
        if k not in self._d.keys() and k not in self.ids:
            raise exc.CandeKeyError(f"can only change existing keys - "
                                    f"{k!s} not in sections;")
        else:
            self._d.__setitem__(k, v)

    def __delitem__(self, k: int) -> None:
        if k in self.ids:
            raise exc.CandeKeyError(f"section name {k!s} must first be removed "
                                    f"from {type(self.seq).__qualname__}")
        self._d.__delitem__(k)

    def __iter__(self) -> Iterator[int]:
        return self._d.__iter__()

    def __len__(self) -> int:
        return self._d.__len__()

    def __repr__(self) -> str:
        return f'NumMapsManager(seq_type={self.seq_type!r}, seq_len={self.seq_len!r}, seq_id={self.seq_id!r})'

    def by_name(self, name: str) -> NumMap[HasNum]:
        return self._d[id(self.seq[name])]

    def renumber(self) -> None:
        """Globalize num attribute values of all the target nodes."""
        start = 1

        num_map: NumMap[HasNum]
        for num_map in self.values():
            num_map.renumber(start)
            start += len(num_map)

    @property
    def seq_id(self) -> int:
        return id(self.seq)

    @property
    def seq_len(self) -> int:
        return sum(skippable_len(s) for s in self.seq.seq_map.values())

    @property
    def seq_type(self) -> str:
        return type(self.seq).__qualname__

    @property
    def ids(self) -> Iterator[Any]:
        """The current section ids for the referenced CANDE item sequence"""
        yield from (id(v) for v in self.seq.seq_map.values())
