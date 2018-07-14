# -*- coding: utf-8 -*-

"""Special tools for working with candeobj types."""

from dataclasses import dataclass, field
from typing import _KT, _VT_co, MutableMapping, _VT, Iterator, _T_co, DefaultDict, Union, Generic, TypeVar, Any, Dict, \
    List
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
    _keys: List[int] = field(init=False)

    def __post_init__(self) -> None:
        seen = set()
        self._keys = [(num, seen.add(num))[0] for num in self.seq if num not in seen]
        self._d = dict(zip(self._keys, itertools.count(self.start)))

    def __getitem__(self, k: int) -> int:
        return self._d.__getitem__(k)

    def __setitem__(self, k: int, v: int) -> None:
        if k in self._keys:
            self._d.__setitem__(k, v)
        else:
            raise exc.CandeKeyError(f"can only change existing keys - {k!s} not"
                                    f" in nums;")

    def __delitem__(self, v: int) -> None:
        self._d.__delitem__(v)
        self._keys.remove(v)

    def __iter__(self) -> Iterator[int]:
        return iter(self._keys)

    def __len__(self) -> int:
        return self._d.__len__()


@dataclass(eq=False)
class NumConverter(MutableMapping[Any, SubConverter]):
    seq: CandeSeq = field(repr=False)
    _d: Dict[_KT, _VT] = field(init=False, repr=False)
    name: str = field(init=False)

    def __post_init__(self):
        self.name = type(self.seq).__qualname__.lower()

        # build node number conversion map and reset node.num attribute
        node_ctr = itertools.count(self.start)
        convert_map = DefaultDict(dict)
        for seq in self.seq.seq_map.values():
            seq_id = id(seq)
            sub_map = convert_map[seq_id]
            for node, num in zip(seq, node_ctr):
                sub_map[node.num] = num
                node.num = num

        self._d = Converter(zip(self.seq.seq_map.keys(), int))

    def __getitem__(self, k: _KT) -> _VT_co:
        return self._d.__getitem__(k)

    def __setitem__(self, k: _KT, v: _VT) -> None:
        self._d.__setitem__(k, v)

    def __delitem__(self, v: _KT) -> None:
        self._d.__delitem__(v)

    def __iter__(self) -> Iterator[_T_co]:
        return self._d.__iter__()

    def __len__(self) -> int:
        return self._d.__len__()
