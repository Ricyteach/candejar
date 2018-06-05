# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""
import types
from typing import Callable, Any, Iterable, Sequence, Mapping, Optional, TypeVar, Union, Type

from ..utilities.collections import KeyedChainView, CollectionConvertingMixin

T = TypeVar("T")


class CandeSequence(CollectionConvertingMixin[T]):
    __slots__ = ()

class KeyedCandeSequence(KeyedChainView[T], CandeSequence):
    __slots__ = ()

# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
candesequence_converter_dict = dict(pipegroups = types.SimpleNamespace,
                                    nodes = types.SimpleNamespace,
                                    elements = types.SimpleNamespace,
                                    boundaries = types.SimpleNamespace,
                                    soilmaterials = types.SimpleNamespace,
                                    interfmaterials = types.SimpleNamespace,
                                    factors = types.SimpleNamespace,
                                    )


def make_candesequence(name: str, value_type: Optional[type] = None) -> Type[CandeSequence]:
    converter = candesequence_converter_dict[name.lower()]
    if value_type is None:
        value_type = converter
    T: Type[CandeSequence] = types.new_class(name, (CandeSequence[value_type],), dict(kwarg_convert = converter))
    return T

PipeGroups = make_candesequence("PipeGroups")
Nodes = make_candesequence("Nodes")
Elements = make_candesequence("Elements")
Boundaries = make_candesequence("Boundaries")
SoilMaterials = make_candesequence("SoilMaterials")
InterfMaterials = make_candesequence("InterfMaterials")
Factors = make_candesequence("Factors")

cande_seq_dict = dict(pipegroups = PipeGroups,
                      nodes = Nodes,
                      elements = Elements,
                      boundaries = Boundaries,
                      soilmaterials = SoilMaterials,
                      interfmaterials = InterfMaterials,
                      factors = Factors,
                      )
