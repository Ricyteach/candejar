# -*- coding: utf-8 -*-

"""Special tools for working with candeobj types."""

from dataclasses import dataclass, field
from typing import MutableMapping, Iterator, Union, TypeVar, Any, Dict
import itertools

from . import exc
from .candeseq import Nodes, Elements, NodesSection, ElementsSection

CandeSeq = TypeVar("CandeSeq", bound=Union[Nodes, Elements])
SectionSeq = TypeVar("SectionSeq", bound=Union[NodesSection, ElementsSection])


@dataclass(eq=False, repr=False)
class SubConverter(MutableMapping[int, int]):
    """Builds a mapping that turns an old item num attribute into a new one
    based on the order. The new new item num attributed begins at the starting
    point, start.
    """
    start: int
    seq: SectionSeq
    _d: Dict[int, int] = field(init=False)

    def __post_init__(self) -> None:
        seen = set()
        keys = [(num, seen.add(num))[0] for num in self.nums if num not in seen]
        self._d = dict(zip(keys, itertools.count(self.start)))

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
        if k in self.nums:
            raise exc.CandeKeyError(f"item num {k!s} must first be removed from {type(self.seq).__qualname__}")
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


@dataclass(eq=False, repr=False)
class NumConverter(MutableMapping[int, SubConverter]):
    """Builds a mapping of SubConverter objects assigned to each section"""
    type_: str = field(init=False)
    seq: CandeSeq = field(repr=False)
    seq_id: int = field(init=False)
    _d: Dict[int, SubConverter] = field(init=False, repr=False)

    def __post_init__(self):
        self.type_ = type(self.seq).__qualname__
        self.seq_id = id(self.seq)
        self._d = dict()

        start = 1
        for section_seq in self.seq.seq_map.values():
            c = self._d[id(section_seq)] = SubConverter(start, section_seq)
            start = len(c)

    def __getitem__(self, k: int) -> SubConverter:
        try:
            return self._d.__getitem__(k)
        except KeyError:
            if k in self.names:
                raise exc.CandeKeyError(f"conversion mapping missing for section name {k!s}")
            raise exc.CandeKeyError(f"section name {k!s} does not appear in {type(self.seq).__qualname__}")

    def __setitem__(self, k: int, v: SubConverter) -> None:
        if k not in self._d.keys() and k not in self.names:
            raise exc.CandeKeyError(f"can only change existing keys - {k!s} not in sections;")
        else:
            self._d.__setitem__(k, v)

    def __delitem__(self, k: int) -> None:
        if k in self.names:
            raise exc.CandeKeyError(f"section name {k!s} must first be removed from {type(self.seq).__qualname__}")
        self._d.__delitem__(k)

    def __iter__(self) -> Iterator[int]:
        return self._d.__iter__()

    def __len__(self) -> int:
        return self._d.__len__()

    def __repr__(self) -> str:
        return f'NumConverter(type_={self.type_!r}, seq_len={self.seq_len!r}, seq_id={self.seq_id!r})'

    @property
    def seq_len(self) -> int:
        return len(self.seq)

    @property
    def names(self) -> Iterator[Any]:
        """The current section names for the referenced CANDE item sequence"""
        yield from self.seq.seq_map.keys()
