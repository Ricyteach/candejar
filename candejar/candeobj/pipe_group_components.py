# -*- coding: utf-8 -*-

"""Module for working with the components that make up cande pipe group type objects."""

from dataclasses import dataclass, field
from typing import ClassVar, Callable, Type

from ..cid import A2, B1Basic, B2Basic, B1Plastic, B2Plastic, B3PlasticASmooth, B3PlasticAGeneral, B3PlasticAProfile, B3bPlasticAProfile, B3PlasticDWSD, B3PlasticDLRFD, B4Plastic
from ..cid import CidLineType
from ..utilities.mixins import child_dispatcher
from .bases import CandeComponent, LinetypeKeyFactory, CandeStr, CandeNum, CandeFloat

class PipeGroupComponent(CandeComponent, key_factory=LinetypeKeyFactory):
    """Base class for all components of pipe group objects

    Each PGC child component is registered with PGC using its `linetype_key` attribute.
    """
    pass

@child_dispatcher("type_")
@dataclass
class PipeGroupGeneralComponent(PipeGroupComponent):
    """Base class for the top level (A2) pipe group component

    The child components are [Aluminum, Basic, Concrete, Plastic, Steel, Conrib, Contube]Component
    """
    _make_reg_key: ClassVar[Callable[[Type[PipeGroupComponent]],CandeStr]] = lambda subcls: subcls.type_.default
    linetype_key: ClassVar[CidLineType] = A2
    type_: CandeStr  # ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE
    num: CandeNum


@dataclass
class BasicComponent(PipeGroupGeneralComponent):
    type_: CandeStr  = field(default="BASIC", repr=False, init=False)


@dataclass
class Basic1Component(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B1Basic
    # ANALYS only
    # repeatable (multiple properties in one pipe group)
    first: CandeNum = 0
    last: CandeNum = 0
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
    mode: CandeNum = 0

# TODO: Finish all aluminium components
@dataclass
class AluminumComponent(PipeGroupGeneralComponent):
    type_: CandeStr  = field(default="ALUMINUM", repr=False, init=False)


# TODO: Finish all steel components
@dataclass
class SteelComponent(PipeGroupGeneralComponent):
    type_: CandeStr  = field(default="STEEL", repr=False, init=False)


@dataclass
class PlasticComponent(PipeGroupGeneralComponent):
    type_: CandeStr  = field(default="PLASTIC", repr=False, init=False)


@child_dispatcher("walltype")
@dataclass
class Plastic1Component(PipeGroupComponent, make_reg_key = lambda subcls: subcls.walltype):
    linetype_key: ClassVar[CidLineType] = B1Plastic
    # GENERAL, SMOOTH, PROFILE
    walltype: CandeStr
    # HDPE, PVC, PP, OTHER
    pipetype: float = "HDPE"
    # 1: Short term, 2: Long term
    duration: CandeNum = 1
    # Small Deformation: 0, Large Deformation: 1, Plus Buckling: 2
    mode: CandeNum = 0


@dataclass
class Plastic1GeneralComponent(Plastic1Component):
    walltype: CandeStr = "GENERAL"

@dataclass
class Plastic1SmoothComponent(Plastic1Component):
    walltype: CandeStr = "SMOOTH"

@dataclass
class Plastic1ProfileComponent(Plastic1Component):
    walltype: CandeStr = "PROFILE"

@dataclass
class Plastic2Component(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B2Plastic
    shortmodulus: CandeFloat = 0.0 # psi
    shortstrength: CandeFloat = 0.0 # psi
    longmodulus: CandeFloat = 0.0 # psi
    longstrength: CandeFloat = 0.0 # psi
    poissons: CandeFloat = 0.3
    density: CandeFloat = 0.0 # pci

@dataclass
class Plastic3SmoothComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticASmooth
    # for ANALYS only
    # WallType = SMOOTH
    height: CandeFloat = 0.0 # in

@dataclass
class Plastic3GeneralComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticAGeneral
    # for ANALYS only
    # WallType = GENERAL
    height: CandeFloat = 0.0 # in
    area: CandeFloat = 0.0 # in2/in
    i: CandeFloat = 0.0 # in4/in
    centroid: CandeFloat = 0.0 # in

@dataclass
class Plastic3ProfileComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticAProfile
    # for ANALYS only
    # WallType = PROFILE
    # repeatable (multiple properties in one pipe group)
    period: CandeFloat = 0.0 # in
    height: CandeFloat = 0.0 # in
    webangle: CandeFloat = 90.0 # degrees
    webthickness: CandeFloat = 0.0 # in
    webk: CandeFloat = 4.0
    # 0 to 4
    numhorizontal: CandeNum = 0
    # 1: include, -1: ignore
    buckling: CandeNum = 1
    first: CandeNum = 0
    last: CandeNum = 1

@dataclass
class Plastic3bAProfileComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3bPlasticAProfile
    # for ANALYS only
    # WallType = PROFILE
    # Required for each NumHorizontal elements in each repeated B3 line
    # 1: inner valley, 2: inner liner, 3: outer crest, 4: outer link
    identifier: CandeNum = 0
    length: CandeFloat = 0.0 # in
    thickness: CandeFloat = 0.0 # in
    supportk: CandeFloat = 4.0

@dataclass
class Plastic3DWSDComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticDWSD
    # for DESIGN only
    # WallType = SMOOTH
    # Non LRFD only
    yieldfs: CandeFloat = 2.0
    bucklingfs: CandeFloat = 3.0
    strainfs: CandeFloat = 2.0
    deflection: CandeFloat = 5.0 # percent
    tensile: CandeFloat = 0.05 # in/in

@dataclass
class Plastic3DLRFDComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B3PlasticDLRFD
    # for DESIGN only
    # WallType = SMOOTH
    # LRFD only
    yield_: CandeFloat = 1.0
    buckling: CandeFloat = 1.0
    strain: CandeFloat = 1.0
    deflection: CandeFloat = 1.0
    tensile: CandeFloat = 1.0

@dataclass
class Plastic4DSmoothLRFDComponent(PipeGroupComponent):
    linetype_key: ClassVar[CidLineType] = B4Plastic
    # for DESIGN only
    # WallType = SMOOTH
    # LRFD only
    yieldϕ: CandeFloat = 1.0
    bucklingϕ: CandeFloat = 1.0
    strainϕ: CandeFloat = 1.0
    deflectionpercent: CandeFloat = 5.0 # percent
    tensileservice: CandeFloat = 0.05 # in/in
