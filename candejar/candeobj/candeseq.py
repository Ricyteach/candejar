# -*- coding: utf-8 -*-

"""All the top level Cande sequence objects"""
from typing import TypeVar, Mapping, MutableMapping, List, ChainMap, overload, Union, Tuple, ValuesView
import collections

from candejar.utilities.collections import DeepChainMap
from .candeseqbase import CandeSection, CandeList, CandeMapSequence
from .parts import PipeGroup, Node, Element, Boundary, Material, Factor
from ..utilities.mixins import GeoMixin
from ..utilities.skip import SkipAttrIterMixin

T=TypeVar("T")
K=TypeVar("K")
V=TypeVar("V")
V_co = TypeVar('V_co', covariant=True)
no_arg = object()


class CandeChainMapError(Exception):
    pass


class CandeChainMapKeyError(KeyError, CandeChainMapError):
    pass


class CandeChainMapTypeError(TypeError, CandeChainMapError):
    pass


class CandeChainMapValueError(ValueError, CandeChainMapError):
    pass


class CandeChainMap(ChainMap[K,V]):
    """A ChainMap with context map being the sections map. Subsequent maps are maps of numbered objects (nodes, elements,
    boundaries, materials, etc)."""
    maps: List[MutableMapping[K, V]]

    def __init__(self, **sections: Mapping[K, V]) -> None:
        if not all(isinstance(section, Mapping) for section in sections.values()):
            raise CandeChainMapTypeError("sections names must be a mapping")
        if not all(isinstance(k, int) for section in sections.values() for k in section.keys()):
            raise CandeChainMapValueError("section objects must be numbered with ints")
        super().__init__(sections, *(section for section in sections.values()))

    def __setitem__(self, key, value) -> None:
        # sections are labeled by a str key
        if isinstance(key, str):
            if not isinstance(value, Mapping):
                raise CandeChainMapTypeError(f"section must be a Mapping, not {type(value).__qualname__!s}")
            if not all(isinstance(k, int) for k in value.keys()):
                raise CandeChainMapValueError(f"section objects must be numbered with ints")
            try:
                del_map = self.maps[0][key]
            except KeyError:
                self.maps.append(value)
            else:
                for i, v in enumerate(self.maps[1:], 1):
                    if del_map is v:
                        self.maps[i] = value
                        break
                else:
                    self.maps[0][key] = del_map  # undo
                    raise CandeChainMapError(f"inconsistent state detected; {key!r} key exists with no map in maps list")
            self.maps[0][key] = value
        # item numbers are labeled by an int
        elif isinstance(key, int):
            for mapping in self.maps[1:]:
                if key in mapping:
                    mapping[key] = value
                    break
            else:
                raise CandeChainMapKeyError(f"item #{key!s} not found; cannot add new keys using CandeChainMap directly")
        # other key types are invalid
        else:
            raise CandeChainMapTypeError(f"key must be a str or int, not {type(key).__qualname__!s}")

    def __delitem__(self, key) -> None:
        # sections are labeled by a str key
        if isinstance(key, str):
            del_map = self.maps[0].pop(key)
            for i, v in enumerate(self.maps[1:], 1):
                if del_map is v:
                    del self.maps[i]
                    break
            else:
                self.maps[0][key] = del_map  # undo
                raise CandeChainMapError(f"inconsistent state detected; {key!r} key was not deleted")
        # item numbers are labeled by an int
        elif isinstance(key, int):
            for mapping in self.maps[1:]:
                if key in mapping:
                    del mapping[key]
                    break
        else:
            raise KeyError(key)

    @property
    def all(self)->DeepChainMap[int, V]:
        """A DeepChainMap containing only the numbered objects (nodes, elements, boundaries, materials, etc)."""
        return DeepChainMap(*self.parents.maps)

    @property
    def objects(self) -> ValuesView[V_co]:
        """A view of all the numbered objects (nodes, elements, boundaries, materials, etc)."""
        try:
            return self._objects
        except AttributeError:
            result = self._objects = self.all.values()
            return result

    @property
    def sections(self)->MutableMapping[str, V]:
        """The sections map."""
        try:
            return self._sections
        except AttributeError:
            result = self._sections = self.maps[0]
            return result

    @overload
    def pop(self, key: K) -> V: ...

    @overload
    def pop(self, key: K, default: Union[V, T]) -> Union[V, T]: ...

    def pop(self, key, default=no_arg):
        sections = self.maps[0]
        # sections are labeled by a str key
        if isinstance(key, str):
            try:
                pop_map = sections.pop(key)
            except KeyError:
                pass
            else:
                for i, v in enumerate(self.maps[1:], 1):
                    if pop_map is v:
                        del self.maps[i]
                        return pop_map
                else:
                    sections[key] = pop_map  # undo
                    raise CandeChainMapError(f"inconsistent state detected; {key!r} key was not deleted")
        # item numbers are labeled by an int
        elif isinstance(key, int):
            for mapping in self.maps[1:]:
                try:
                    return mapping.pop(key)
                except KeyError:
                    pass

        if default is no_arg:
            raise KeyError(key)
        else:
            return default

    def popitem(self) -> Tuple[K, V]:
        """Only pops sections."""
        key, item = self.sections.popitem()
        if len(self.maps)>1:
            del self.maps[-1]
        else:
            self.maps[0][key] = item  # undo
            raise CandeChainMapError(f"inconsistent state detected; {key!r} key was not deleted")
        return key, item


############################
#  CandeSection sequences  #
############################

geo_type_lookup = dict(nodes="MultiPoint",
                       elements="MultiPolygon",
                       boundaries="MultiNode",
                       )


class NodesSection(GeoMixin, SkipAttrIterMixin[Node], CandeSection[Node],
                   converter=Node, geo_type=geo_type_lookup["nodes"]):
    skippable_attr = "num"


class ElementsSection(GeoMixin, SkipAttrIterMixin[Element], CandeSection[Element],
                      converter=Element, geo_type=geo_type_lookup["elements"]):
    skippable_attr = "num"


class BoundariesSection(GeoMixin, CandeSection[Boundary], converter=Boundary,
                        geo_type=geo_type_lookup["boundaries"]):
    pass


class MaterialsSection(SkipAttrIterMixin[Material], CandeList[Material],
                       converter=Material):
    """NOTE: the only materials sections are soil, interface, and composite
    (for link elements)."""
    skippable_attr = "num"


#########################
#  CandeList sequences  #
#########################

class PipeGroups(CandeList[PipeGroup], converter=PipeGroup):
    pass


class Factors(CandeList[Factor], converter=Factor):
    pass


##########################
#  Materials sequences  #
##########################

class SoilMaterials(MaterialsSection):
    pass


class InterfMaterials(MaterialsSection):
    pass


class CompositeMaterials(MaterialsSection):
    pass


################################
#  CandeMapSequence sequences  #
################################

class Nodes(CandeMapSequence[Node]):
    seq_type = NodesSection


class Elements(CandeMapSequence[Element]):
    seq_type = ElementsSection


class Boundaries(CandeMapSequence[Boundary]):
    seq_type = BoundariesSection


class Materials(CandeMapSequence[Material]):
    seq_type = MaterialsSection


#######################
#  Element sequences  #
#######################

class PipeElements(Elements):
    pass


class SoilElements(Elements):
    pass


class InterfElements(Elements):
    pass


###############################
#  CANDE sequence registries  #
###############################

cande_seq_dict = dict(zip("pipegroups nodes elements pipeelements soilelements "
                          "interfelements boundaries materials soilmaterials "
                          "interfmaterials compositematerials factors".split(),
                          (PipeGroups, Nodes, Elements, PipeElements,
                           SoilElements, InterfElements, Boundaries, Materials,
                           SoilMaterials, InterfMaterials, CompositeMaterials, Factors)))


cande_section_dict = dict(zip("nodessection elementssection boundariessection".split(),
                              (NodesSection, ElementsSection, BoundariesSection)))
