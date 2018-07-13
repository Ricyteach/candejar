# -*- coding: utf-8 -*-

"""Special tools for working with candeobj types."""

from abc import ABC
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Sequence, Any, Iterable, overload, Optional, Mapping, _KT, _VT_co, MutableMapping, \
    _VT, Iterator, _T_co, DefaultDict

import itertools

from ..candeobj import exc
from .collections import KeyedChainView, ConvertingList

T = TypeVar("T")


class CandeList(ConvertingList[T]):
    """Extends ConvertingList with a better repr and for specialized subclassing"""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({super().__repr__()})"


class CandeSection(CandeList):
    """Parent class for all CANDE section objects"""
    __slots__ = ()


geo_type_lookup = dict(nodes="MultiPoint",
                       elements="MultiPolygon",
                       boundaries="MultiNode",
                       )


class CandeMapSequence(KeyedChainView[T]):
    """Extends KeyedChainView to utilize a specified type for the sub-sequences.

    The specified type is stored as obj.seq_type
    """
    __slots__ = ()

    def __init_subclass__(cls, **kwargs):
        try:
            cls.seq_type = kwargs.pop("seq_type")
        except KeyError:
            # seq_type is option so children of subclasses can be created with their own seq_type
            pass
        super().__init_subclass__(**kwargs)


    def __init__(self, seq_map: Optional[Mapping[Any, CandeList[T]]] = None, **kwargs: Iterable[T]) -> None:
        if type(self) is CandeMapSequence:
            raise exc.CandeTypeError(f"CandeMapSequence cannot be instantiated directly")
        if not hasattr(self, "seq_type"):
            raise exc.CandeAttributeError(f"{type(self).__qualname__} requires a 'seq_type' attribute for instantiation")
        if not hasattr(self.seq_type, "converter"):
            raise exc.CandeAttributeError(f"{type(self).__qualname__}.seq_type object attribute requires a 'converter' "
                                          f"attribute for instantiation")
        if seq_map is None:
            seq_map = {}
        for k, v in seq_map.copy().items():
            seq_map[k] = self.seq_type(v) if not isinstance(v, self.seq_type) else v
        seq_map.update((k, v if isinstance(v, self.seq_type) else self.seq_type(v)) for k,v in kwargs.items())
        super().__init__(seq_map)

    @overload
    def __setitem__(self, i: int, v: T) -> None:
        ...

    @overload
    def __setitem__(self, s: slice, v: Iterable[T]) -> None:
        ...

    @overload
    def __setitem__(self, k: Any, v: Sequence[T]) -> None:
        ...

    def __setitem__(self, x, v):
        if not (isinstance(x, slice) or isinstance(x, int)):
            v = v if isinstance(v, self.seq_type) else self.seq_type(v)
        super().__setitem__(x, v)


# For typing purposes only
class CandeSequence(ABC, Generic[T]):
    pass


CandeSequence.register(CandeList)
CandeSequence.register(CandeMapSequence)


S = TypeVar("S", bound=CandeSequence)


@dataclass(eq=False)
class Converter(Generic[S, _KT, _VT], MutableMapping[]):
    seq: S = field(repr=False)
    start: int = 1
    _d: MutableMapping = field(init=False, repr=False)


@dataclass(eq=False)
class SubConverter(Converter[int, int]):



@dataclass(eq=False)
class NumConverter(Converter[int, SubConverter]):
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
