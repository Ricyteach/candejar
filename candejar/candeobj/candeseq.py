# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

import functools
import types
from abc import ABC
from typing import Callable, Any, Optional, TypeVar, Type, List

from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView, CollectionConvertingMixin

T = TypeVar("T")


class CandeListSequence(CollectionConvertingMixin[T], List[T]):
    __slots__ = ()


class CandeMapSequence(CollectionConvertingMixin[T], KeyedChainView[T]):
    __slots__ = ()


class CandeSequence(ABC):
    pass

CandeSequence.register(CandeListSequence)
CandeSequence.register(CandeMapSequence)

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
    cls: Type[CandeSequence] = types.new_class(name, (CandeMapSequence[value_type],), dict(kwarg_convert=wrapped_converter))
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
