# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

import functools
import types
from abc import ABC
from typing import Callable, Any, Optional, TypeVar, Type, overload, Iterable, Sequence, Mapping, Generic, Tuple

from . import exc
from ..candeobj.level3 import Node, Element, Boundary
from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView, ConvertingList
from ..utilities.mixins import GeoMixin

T = TypeVar("T")


class CandeList(ConvertingList[T]):
    """Extends ConvertingList with a better repr and for specialized subclassing"""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({super().__repr__()})"


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


# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
# TODO: maybe make these more robust so filters out unnecessary keyword arguments...?
candesequence_item_converter_dict = dict(pipegroups=types.SimpleNamespace,
                                         nodes=Node,
                                         elements=Element,
                                         pipeelements=Element,
                                         soilelements=Element,
                                         interfelements=Element,
                                         boundaries=Boundary,
                                         materials=types.SimpleNamespace,
                                         soilmaterials=types.SimpleNamespace,
                                         interfmaterials=types.SimpleNamespace,
                                         factors=types.SimpleNamespace,
                                         )


def mapify_and_unpack_decorator(f: Callable[..., Any]) -> Callable[[Any], Any]:
    @functools.wraps(f)
    def wrapped(v: Any) -> Any:
        return f(**shallow_mapify(v))
    return wrapped


cande_seq_dict = dict()


def make_cande_list_class(name: str, value_type: Optional[T] = None) -> Type[CandeSequence[T]]:
    # get the item converter from the dictionary
    converter = candesequence_item_converter_dict[name.lower()]
    # the value_type is just for type annotation
    if value_type is None:
        if isinstance(converter, type):
            value_type = converter
        else:
            raise exc.CandeTypeError("container type needs to be specified for type checker when using a non-type as a converter")
    # change the converter so it accepts a single argument instead of an unpacked map
    wrapped_converter = mapify_and_unpack_decorator(converter)
    cls: Type[CandeSequence] = types.new_class(name, (CandeList[value_type],), dict(converter=wrapped_converter))
    # add the new cande_seq class to cande_seq_dict
    cande_seq_dict[name.lower()] = cls
    return cls


cande_section_dict = dict()


def make_cande_map_seq_and_list_class(section_name: str, name: str, *, value_type: Optional[T] = None) -> Tuple[Type[CandeMapSequence[T]], Type[CandeList[T]]]:
    # get the item converter from the dictionary
    converter = candesequence_item_converter_dict[name.lower()]
    # the value_type is just for type annotation
    if value_type is None:
        if isinstance(converter, type):
            value_type = converter
        else:
            raise exc.CandeTypeError("container type needs to be specified for type checker when using a non-type as a converter")
    # change the converter so it accepts a single argument instead of an unpacked map
    try:
        section_cls = cande_section_dict[section_name]
    except KeyError:
        wrapped_converter = mapify_and_unpack_decorator(converter)
        try:
            # check if appears in geo_type registry
            geo_type = geo_type_lookup[section_name]
        except KeyError:
            # not a geo_type
            section_cls: Type[CandeList] = types.new_class(f"{name}Section", (CandeList[value_type],),
                                                           dict(converter=wrapped_converter))
        else:
            # is geo_type
            section_cls: Type[CandeList] = types.new_class(f"{name}Section", (GeoMixin,CandeList[value_type]),
                                                           dict(converter=wrapped_converter, geo_type=geo_type))
        # add the new cande_section class to cande_section_dict
        cande_section_dict[section_name] = section_cls

    # set default parent class and exec_body
    parent = CandeMapSequence[value_type]
    exec_body = lambda ns: ns
    # make Elements the parent class for PipeElements, SoilElements, and InterfElements
    if section_name == "elements" and name.lower() != "elements":
        parent = cande_seq_dict["elements"]
    # add elements methods using exec_body
    if section_name == "elements" and name.lower() == "elements":
        pass
    cls: Type[CandeMapSequence] = types.new_class(name, (parent,), dict(seq_type=section_cls), exec_body=exec_body)
    # add the new cande_map class to cande_seq_dict
    cande_seq_dict[name.lower()] = cls
    return cls, section_cls


PipeGroups = make_cande_list_class("PipeGroups")
Nodes, NodesSection = make_cande_map_seq_and_list_class("nodes", "Nodes")
Elements, ElementsSection = make_cande_map_seq_and_list_class("elements", "Elements")
PipeElements, _ = make_cande_map_seq_and_list_class("elements", "PipeElements")
SoilElements, _ = make_cande_map_seq_and_list_class("elements", "SoilElements")
InterfElements, _ = make_cande_map_seq_and_list_class("elements", "InterfElements")
Boundaries, BoundariesSection = make_cande_map_seq_and_list_class("boundaries", "Boundaries")
Materials, _ = make_cande_map_seq_and_list_class("materials", "Materials")
SoilMaterials = make_cande_list_class("SoilMaterials")
InterfMaterials = make_cande_list_class("InterfMaterials")
Factors = make_cande_list_class("Factors")
