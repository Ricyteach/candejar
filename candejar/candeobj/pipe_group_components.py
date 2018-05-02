# -*- coding: utf-8 -*-

"""Module for working with the components that make up cande pipe group type objects."""

from dataclasses import dataclass
from typing import ClassVar

from ..cid import A2, B1Basic, B2Basic, B1Plastic, B2Plastic, B3PlasticASmooth, B3PlasticAGeneral, B3PlasticAProfile, B3bPlasticAProfile, B3PlasticDWSD, B3PlasticDLRFD, B4Plastic
from ..cid import CidLineType
from ..utilities.mixins import child_dispatcher
from .bases import CandeComponent, LinetypeKeyFactory

class PipeGroupComponent(CandeComponent, key_factory=LinetypeKeyFactory):
    """Base class for all components of pipe group objects

    Each PGC child component is registered with PGC using its `linetype_key` attribute.
    """
    pass

@child_dispatcher("type_")
@dataclass
class PipeGroupGeneralComponent(PipeGroupComponent, make_reg_key = lambda subcls: subcls.type_):
    """Base class for the top level (A2) pipe group component

    The child components are [Aluminum, Basic, Concrete, Plastic, Steel, Conrib, Contube]Component
    """
    linetype_key: ClassVar[CidLineType] = A2
    type_: str  # ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE


@dataclass
class BasicComponent(PipeGroupGeneralComponent):
    type_: str  = "BASIC"

@dataclass
class Basic1Component(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B1Basic
    # ANALYS only
    # repeatable (multiple properties in one pipe group)
    first: int = 0
    last: int = 0
    modulus: float = 0.0 # psi
    poissons: float = 0.0
    area: float = 0.0 # in2/in
    i: float = 0.0 # in4/in
    load: float = 0.0 # lbs/in

@dataclass
class Basic2Component(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B2Basic
    # for ANALYS mode only
    # Small Deformation: 0, Large Deformation: 1, Plus Buckling: 2
    mode: int = 0

# TODO: Finish all aluminium components
@dataclass
class AluminumComponent(PipeGroupGeneralComponent):
    type_: str  = "ALUMINUM"


# TODO: Finish all steel components
@dataclass
class SteelComponent(PipeGroupGeneralComponent):
    type_: str  = "STEEL"


@dataclass
class PlasticComponent(PipeGroupGeneralComponent):
    type_: str  = "PLASTIC"


@child_dispatcher("walltype")
@dataclass
class Plastic1Component(PipeGroupComponent, make_reg_key = lambda subcls: subcls.walltype):
    linetype_key: ClassVar[CidLineType] = B1Plastic
    # GENERAL, SMOOTH, PROFILE
    walltype: str
    # HDPE, PVC, PP, OTHER
    pipetype: float = "HDPE"
    # 1: Short term, 2: Long term
    duration: int = 1
    # Small Deformation: 0, Large Deformation: 1, Plus Buckling: 2
    mode: int = 0


@dataclass
class Plastic1GeneralComponent(Plastic1Component):
    walltype: str = "GENERAL"

@dataclass
class Plastic1SmoothComponent(Plastic1Component):
    walltype: str = "SMOOTH"

@dataclass
class Plastic1ProfileComponent(Plastic1Component):
    walltype: str = "PROFILE"

@dataclass
class Plastic2Component(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B2Plastic
    shortmodulus: float = 0.0 # psi
    shortstrength: float = 0.0 # psi
    longmodulus: float = 0.0 # psi
    longstrength: float = 0.0 # psi
    poissons: float = 0.3
    density: float = 0.0 # pci

@dataclass
class Plastic3SmoothComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticASmooth
    # for ANALYS only
    # WallType = SMOOTH
    height: float = 0.0 # in

@dataclass
class Plastic3GeneralComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticAGeneral
    # for ANALYS only
    # WallType = GENERAL
    height: float = 0.0 # in
    area: float = 0.0 # in2/in
    i: float = 0.0 # in4/in
    centroid: float = 0.0 # in

@dataclass
class Plastic3ProfileComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticAProfile
    # for ANALYS only
    # WallType = PROFILE
    # repeatable (multiple properties in one pipe group)
    period: float = 0.0 # in
    height: float = 0.0 # in
    webangle: float = 90.0 # degrees
    webthickness: float = 0.0 # in
    webk: float = 4.0
    # 0 to 4
    numhorizontal: int = 0
    # 1: include, -1: ignore
    buckling: int = 1
    first: int = 0
    last: int = 1

@dataclass
class Plastic3bAProfileComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3bPlasticAProfile
    # for ANALYS only
    # WallType = PROFILE
    # Required for each NumHorizontal elements in each repeated B3 line
    # 1: inner valley, 2: inner liner, 3: outer crest, 4: outer link
    identifier: int = 0
    length: float = 0.0 # in
    thickness: float = 0.0 # in
    supportk: float = 4.0

@dataclass
class Plastic3DWSDComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticDWSD
    # for DESIGN only
    # WallType = SMOOTH
    # Non LRFD only
    yieldfs: float = 2.0
    bucklingfs: float = 3.0
    strainfs: float = 2.0
    deflection: float = 5.0 # percent
    tensile: float = 0.05 # in/in

@dataclass
class Plastic3DLRFDComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticDLRFD
    # for DESIGN only
    # WallType = SMOOTH
    # LRFD only
    yield_: float = 1.0
    buckling: float = 1.0
    strain: float = 1.0
    deflection: float = 1.0
    tensile: float = 1.0

@dataclass
class Plastic4DSmoothLRFDComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B4Plastic
    # for DESIGN only
    # WallType = SMOOTH
    # LRFD only
    yieldϕ: float = 1.0
    bucklingϕ: float = 1.0
    strainϕ: float = 1.0
    deflectionpercent: float = 5.0 # percent
    tensileservice: float = 0.05 # in/in


