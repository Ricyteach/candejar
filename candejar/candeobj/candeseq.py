# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

import functools
import types
from abc import ABC
from typing import Callable, Any, Optional, TypeVar, Type, List, overload, Iterable, Sequence, Mapping

from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView, CollectionConvertingMixin

T = TypeVar("T")


class CandeSectionSequence(List[T]):
    pass


class CandeListSequence(CollectionConvertingMixin[T], List[T]):
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({super().__repr__()})"


class CandeMapSequence(CollectionConvertingMixin[T], KeyedChainView[T]):
    __slots__ = ()

    def __init__(self, seq_map: Optional[Mapping[Any, Sequence[T]]] = None, **kwargs: Iterable[T]) -> None:
        super().__init__(seq_map, **kwargs)
        for k,v in self.seq_map.copy().items():
            if not isinstance(v, CandeSectionSequence):
                del self[k]
                super().__setitem__(k, CandeSectionSequence(v))

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
        super().__setitem__(x, v)
        new_v = self[x]
        if not (isinstance(x, slice) or isinstance(x, int)):
            if not isinstance(new_v, CandeSectionSequence):
                del self[x]
                super().__setitem__(x, CandeSectionSequence(v))


class CandeSequence(ABC):
    pass


CandeSequence.register(CandeListSequence)
CandeSequence.register(CandeMapSequence)
CandeSequence.register(CandeSectionSequence)

# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
candesequence_item_converter_dict = dict(pipegroups=types.SimpleNamespace,
                                         nodes=types.SimpleNamespace,
                                         elements=types.SimpleNamespace,
                                         boundaries=types.SimpleNamespace,
                                         soilmaterials=types.SimpleNamespace,
                                         interfmaterials=types.SimpleNamespace,
                                         factors=types.SimpleNamespace,
                                         )


def mapify_and_unpack_decorator(f: Callable[..., Any]) -> Callable[[Any], Any]:
    @functools.wraps(f)
    def wrapped(v: Any) -> Any:
        return f(**shallow_mapify(v))
    return wrapped


def make_cande_sequence_class(name: str, value_type: Optional[T] = None) -> Type[CandeSequence]:
    # get the item converter from the dictionary
    converter = candesequence_item_converter_dict[name.lower()]
    # the value_type is just for type annotation
    if value_type is None:
        if isinstance(converter, type):
            value_type = converter
        else:
            raise TypeError("CandeSequence container type needs to be specified for type checker when using a non-type as a converter")
    # change the converter so it accepts a single argument instead of an unpacked map
    wrapped_converter = mapify_and_unpack_decorator(converter)
    if name in "Nodes Elements Boundaries".split():
        CandeSequenceType = CandeMapSequence
    elif name in "PipeGroups SoilMaterials InterfMaterials Factors".split():
        CandeSequenceType = CandeListSequence
    else:
        raise ValueError(f"invalid cande object sequence attribute name: {name!s}")
    cls: Type[CandeSequence] = types.new_class(name, (CandeSequenceType[value_type],), dict(kwarg_convert=wrapped_converter))
    return cls


PipeGroups = make_cande_sequence_class("PipeGroups")
Nodes = make_cande_sequence_class("Nodes")
Elements = make_cande_sequence_class("Elements")
Boundaries = make_cande_sequence_class("Boundaries")
SoilMaterials = make_cande_sequence_class("SoilMaterials")
InterfMaterials = make_cande_sequence_class("InterfMaterials")
Factors = make_cande_sequence_class("Factors")

cande_seq_dict = dict(pipegroups=PipeGroups,
                      nodes=Nodes,
                      elements=Elements,
                      boundaries=Boundaries,
                      soilmaterials=SoilMaterials,
                      interfmaterials=InterfMaterials,
                      factors=Factors,
                      )
