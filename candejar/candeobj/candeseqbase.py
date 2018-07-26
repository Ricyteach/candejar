# -*- coding: utf-8 -*-

"""The interface for Cande sequence objects expected by the candeobj module."""

import functools
from typing import Callable, Any, Optional, TypeVar, overload, Iterable, \
    Sequence, Mapping

from . import exc
from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView, ConvertingList

T = TypeVar("T")


def mapify_and_unpack_decorator(f: Callable[..., Any]) -> Callable[[Any], Any]:
    @functools.wraps(f)
    def wrapped(v: Any) -> Any:
        return f(**shallow_mapify(v))
    return wrapped


class CandeList(ConvertingList[T]):
    """Extends ConvertingList with a better repr and for specialized subclassing"""
    __slots__ = ()

    def __init_subclass__(cls, **kwargs: Any) -> None:
        try:
            # change the converter so it accepts a single argument instead of an unpacked map
            decorated_converter = mapify_and_unpack_decorator(kwargs.pop("converter"))
        except KeyError:
            super().__init_subclass__(**kwargs)
        else:
            super().__init_subclass__(converter=decorated_converter, **kwargs)

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({super().__repr__()})"


class CandeSection(CandeList[T]):
    """Parent class for all CANDE section objects"""
    __slots__ = ()


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
