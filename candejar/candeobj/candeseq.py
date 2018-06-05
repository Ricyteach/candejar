# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

import functools
import types
from typing import Callable, Any, Optional, TypeVar, Type, List

from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView, CollectionConvertingMixin

T = TypeVar("T")


class CandeSequence(CollectionConvertingMixin[T], List[T]):
    __slots__ = ()


class CandeMapSequence(KeyedChainView[T]):
    __slots__ = ()


# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
candesequence_converter_dict = dict(pipegroups=types.SimpleNamespace,
                                    nodes=types.SimpleNamespace,
                                    elements=types.SimpleNamespace,
                                    boundaries=types.SimpleNamespace,
                                    soilmaterials=types.SimpleNamespace,
                                    interfmaterials=types.SimpleNamespace,
                                    factors=types.SimpleNamespace,
                                    )


def mapify_and_unpack_decorator(f: Callable[[Any], Any]):
    @functools.wraps(f)
    def wrapped(v):
        return f(**shallow_mapify(v))
    return wrapped


def make_cande_sequence(name: str, value_type: Optional[type] = None) -> Type[CandeSequence]:
    # get the converter from the dictionary
    converter = candesequence_converter_dict[name.lower()]
    # the value_type is just for type annotation
    if value_type is None:
        if isinstance(converter, type):
            value_type = converter
        else:
            raise TypeError("CandeSequence container type needs to be specified when using a none type as a converter")
    # change the converter so it accepts an unpacked map instead of a single argument
    wrapped_converter = mapify_and_unpack_decorator(converter)
    cls: Type[CandeSequence] = types.new_class(name, (CandeSequence[value_type],), dict(kwarg_convert=wrapped_converter))
    return cls


PipeGroups = make_cande_sequence("PipeGroups")
Nodes = make_cande_sequence("Nodes")
Elements = make_cande_sequence("Elements")
Boundaries = make_cande_sequence("Boundaries")
SoilMaterials = make_cande_sequence("SoilMaterials")
InterfMaterials = make_cande_sequence("InterfMaterials")
Factors = make_cande_sequence("Factors")

cande_seq_dict = dict(pipegroups=PipeGroups,
                      nodes=Nodes,
                      elements=Elements,
                      boundaries=Boundaries,
                      soilmaterials=SoilMaterials,
                      interfmaterials=InterfMaterials,
                      factors=Factors,
                      )
