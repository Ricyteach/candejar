# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

import functools
import types
from abc import ABC
from typing import Callable, Any, Optional, TypeVar, Type, overload, Iterable, Sequence, Mapping, Generic, Tuple

from . import exc
from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView, ConvertingList

T = TypeVar("T")


class CandeList(ConvertingList[T]):
    """Extends ConvertingList with a better repr and for specialized subclassing"""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({super().__repr__()})"


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

# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
# TODO: maybe make these more robust so filters out unnecessary keyword arguments...?
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


# noinspection PyPep8Naming
def make_cande_sequence_class(name: str, value_type: Optional[T] = None) -> Tuple[Type[CandeSequence], Optional[type]]:
    # get the item converter from the dictionary
    converter = candesequence_item_converter_dict[name.lower()]
    # the value_type is just for type annotation
    if value_type is None:
        if isinstance(converter, type):
            value_type = converter
        else:
            raise exc.CandeTypeError("CandeSequence container type needs to be specified for type checker when using a "
                                     "non-type as a converter")
    # change the converter so it accepts a single argument instead of an unpacked map
    wrapped_converter = mapify_and_unpack_decorator(converter)
    if name in "Nodes Elements Boundaries".split():
        CandeSequenceType = CandeMapSequence[value_type]
        subseq_cls = types.new_class(f"{name}Section", (CandeList[value_type],), dict(converter=wrapped_converter))
        kwds_dict = dict(seq_type=subseq_cls)
    elif name in "PipeGroups SoilMaterials InterfMaterials Factors".split():
        CandeSequenceType = CandeList[value_type]
        subseq_cls = None
        kwds_dict = dict(converter=wrapped_converter)
    else:
        raise exc.CandeValueError(f"invalid cande object sequence attribute name: {name!s}")
    cls: Type[CandeSequence] = types.new_class(name, (CandeSequenceType,), kwds_dict)
    return cls, subseq_cls


PipeGroups, _ = make_cande_sequence_class("PipeGroups")
Nodes, NodesSection = make_cande_sequence_class("Nodes")
Elements, ElementsSection = make_cande_sequence_class("Elements")
Boundaries, BoundariesSection = make_cande_sequence_class("Boundaries")
SoilMaterials, _ = make_cande_sequence_class("SoilMaterials")
InterfMaterials, _ = make_cande_sequence_class("InterfMaterials")
Factors, _ = make_cande_sequence_class("Factors")

cande_seq_dict = dict(pipegroups=PipeGroups,
                      nodes=Nodes,
                      elements=Elements,
                      boundaries=Boundaries,
                      soilmaterials=SoilMaterials,
                      interfmaterials=InterfMaterials,
                      factors=Factors,
                      )


cande_section_dict = dict(nodes=NodesSection,
                          elements=ElementsSection,
                          boundaries=BoundariesSection,
                          )
