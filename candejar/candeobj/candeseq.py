# -*- coding: utf-8 -*-

"""All the top level Cande sequence objects"""

from .candeseqbase import CandeSection, CandeList, CandeMapSequence
from .parts import PipeGroup, Node, Element, Boundary, Material, Factor
from ..utilities.mixins import GeoMixin
from ..utilities.skip import SkippableIterMixin


############################
#  CandeSection sequences  #
############################

geo_type_lookup = dict(nodes="MultiPoint",
                       elements="MultiPolygon",
                       boundaries="MultiNode",
                       )


class NodesSection(GeoMixin, SkippableIterMixin[Node], CandeSection[Node],
                   converter=Node, geo_type=geo_type_lookup["nodes"]):
    skippable_attr = "num"


class ElementsSection(GeoMixin, SkippableIterMixin[Element], CandeSection[Element],
                      converter=Element, geo_type=geo_type_lookup["elements"]):
    skippable_attr = "num"


class BoundariesSection(GeoMixin, CandeSection[Boundary], converter=Boundary,
                        geo_type=geo_type_lookup["boundaries"]):
    pass


class MaterialsSection(SkippableIterMixin[Material], CandeList[Material],
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
