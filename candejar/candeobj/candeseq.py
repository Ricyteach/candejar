# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

import functools
import types
from typing import Callable, Any, Optional, TypeVar, overload, Iterable, Sequence, Mapping

from . import exc
from ..candeobj.level3 import Node, Element, Boundary
from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView, ConvertingList
from ..utilities.mixins import GeoMixin

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


# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
# TODO: maybe make these more robust so filters out unnecessary keyword arguments...?
item_converters = dict(pipegroups=types.SimpleNamespace,
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


############################
#  CandeSection sequences  #
############################

class NodesSection(GeoMixin, CandeSection[item_converters["nodes"]],
                   converter=item_converters["nodes"],
                   geo_type=geo_type_lookup["nodes"]):
    pass


class ElementsSection(GeoMixin, CandeSection[item_converters["elements"]],
                      converter=item_converters["elements"],
                      geo_type=geo_type_lookup["elements"]):
    pass


class BoundariesSection(GeoMixin, CandeSection[item_converters["boundaries"]],
                        converter=item_converters["boundaries"],
                        geo_type=geo_type_lookup["boundaries"]):
    pass


#########################
#  CandeList sequences  #
#########################

class PipeGroups(CandeList[item_converters["pipegroups"]],
                 converter=item_converters["pipegroups"], ):
    pass


class Materials(CandeList[item_converters["materials"]],
                converter=item_converters["materials"], ):
    pass


class Factors(CandeList[item_converters["factors"]],
              converter=item_converters["factors"], ):
    pass


##########################
#  Materials sequences  #
##########################

class SoilMaterials(Materials, converter=item_converters["soilmaterials"]):
    pass


class InterfMaterials(Materials, converter=item_converters["interfmaterials"]):
    pass


################################
#  CandeMapSequence sequences  #
################################

class Nodes(CandeMapSequence[item_converters["nodes"]]):
    seq_type = NodesSection


class Elements(CandeMapSequence[item_converters["elements"]]):
    seq_type = ElementsSection

def make_cande_map_seq_and_list_class(section_name: str, name: str, *, value_type: Optional[T] = None) -> Tuple[Type[CandeMapSequence[T]], Type[CandeList[T]]]:
    # get the item converter from the dictionary
    converter = item_converters[name.lower()]
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
            section_cls: Type[CandeSection] = types.new_class(f"{name}Section", (CandeSection[value_type],),
                                                              dict(converter=wrapped_converter))
        else:
            # is geo_type
            section_cls: Type[CandeSection] = types.new_class(f"{name}Section", (GeoMixin, CandeSection[value_type]),
                                                              dict(converter=wrapped_converter, geo_type=geo_type))
        # add the new cande_section class to cande_section_dict
        cande_section_dict[section_name] = section_cls

class Boundaries(CandeMapSequence[item_converters["boundaries"]]):
    seq_type = BoundariesSection


#######################
#  Element sequences  #
#######################

class PipeElements(Elements):
    pass


class SoilElements(Elements):
    pass


class InterfElements(Elements):
    pass


cande_seq_dict = dict(zip("pipegroups nodes elements pipeelements soilelements "
                          "interfelements boundaries materials soilmaterials "
                          "interfmaterials factors".split(),
                          (PipeGroups, Nodes, Elements, PipeElements,
                           SoilElements, InterfElements, Boundaries, Materials,
                           SoilMaterials, InterfMaterials, Factors)))


cande_section_dict = dict(zip("nodessection elementssection boundariessection".split(),
                              (NodesSection, ElementsSection, BoundariesSection)))
