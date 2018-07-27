# -*- coding: utf-8 -*-

"""Module for working with the components that make up cande pipe group type objects."""

from dataclasses import dataclass, field
from typing import ClassVar, Callable, Type, TypeVar, Generic

from ...cid import A2, B1Basic, B2Basic, B1Plastic, B2Plastic, B3PlasticASmooth, B3PlasticAGeneral, B3PlasticAProfile, \
    B3bPlasticAProfile, B3PlasticDWSD, B3PlasticDLRFD, B4Plastic
from ...cid import CidLineType
from ...utilities.mixins import child_dispatcher
from .bases import CandeComponent, LinetypeKeyFactory, CandeStr, CandeNum, CandeFloat

PGrpSubcls = TypeVar("PGrpSubcls", bound="PipeGroupComponent")
PGrpSubclsChild = TypeVar("PGrpSubclsChild", bound=PGrpSubcls)


@dataclass
class PipeGroupComponent(Generic[PGrpSubcls], CandeComponent["PipeGroupComponent"], key_factory=LinetypeKeyFactory):
    """Base class for all components of pipe group objects

    Each PGC child component is registered with PGC using its `linetype_key` attribute.
    """

    @classmethod
    def getsubcls(cls: Type[PGrpSubcls], key: CidLineType) -> Type[PGrpSubclsChild]:
        """Get the pipe group component corresponding to the cid line type"""
        return super().getsubcls(key)


PGrpGenSubcls = TypeVar("PGrpGenSubcls", bound="PipeGroupGeneralComponent")
PGrpGenSubclsChild = TypeVar("PGrpGenSubclsChild", bound=PGrpGenSubcls)


@child_dispatcher("type_")
@dataclass
class PipeGroupGeneralComponent(Generic[PGrpGenSubcls], PipeGroupComponent["PipeGroupGeneralComponent"]):
    """Base class for the top level (A2) pipe group component

    The child components are [Aluminum, Basic, Concrete, Plastic, Steel, Conrib, Contube]Component
    """
    _make_reg_key: ClassVar[Callable[[Type[PGrpGenSubcls]], CandeStr]] = lambda subcls: subcls.type_.default.lower()
    linetype_key: ClassVar[CidLineType] = A2
    type_: CandeStr  # ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE
    num: CandeNum = 0

    @classmethod
    def getsubcls(cls: Type[PGrpGenSubcls], key: CidLineType) -> Type[PGrpGenSubclsChild]:
        """Get the non case-sensitive pipe group component from the key"""
        return super().getsubcls(key.lower())


@dataclass
class BasicComponent(PipeGroupGeneralComponent["BasicComponent"]):
    type_: CandeStr = field(default="BASIC", repr=False)


@dataclass
class Basic1Component(PipeGroupComponent["Basic1Component"]):
    linetype_key: ClassVar[CidLineType] = B1Basic
    # ANALYS only
    # repeatable (multiple properties in one pipe group)
    first: CandeNum = 0
    last: CandeNum = 0
    modulus: float = 0.0  # psi
    poissons: float = 0.0
    area: float = 0.0  # in2/in
    i: float = 0.0  # in4/in
    load: float = 0.0  # lbs/in


@dataclass
class Basic2Component(PipeGroupComponent["Basic2Component"]):
    linetype_key: ClassVar[CidLineType] = B2Basic
    # for ANALYS mode only
    # Small Deformation: 0, Large Deformation: 1, Plus Buckling: 2
    mode: CandeNum = 0


# TODO: Finish all aluminium components
@dataclass
class AluminumComponent(PipeGroupGeneralComponent["AluminumComponent"]):
    type_: CandeStr = field(default="ALUMINUM", repr=False)


# TODO: Finish all steel components
@dataclass
class SteelComponent(PipeGroupGeneralComponent["SteelComponent"]):
    type_: CandeStr = field(default="STEEL", repr=False)


@dataclass
class PlasticComponent(PipeGroupGeneralComponent["PlasticComponent"]):
    type_: CandeStr = field(default="PLASTIC", repr=False)


@child_dispatcher("walltype")
@dataclass
class Plastic1Component(PipeGroupComponent["Plastic1Component"], make_reg_key=lambda subcls: subcls.walltype):
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
class Plastic2Component(PipeGroupComponent["Plastic2Component"]):
    linetype_key: ClassVar[CidLineType] = B2Plastic
    shortmodulus: CandeFloat = 0.0  # psi
    shortstrength: CandeFloat = 0.0  # psi
    longmodulus: CandeFloat = 0.0  # psi
    longstrength: CandeFloat = 0.0  # psi
    poissons: CandeFloat = 0.3
    density: CandeFloat = 0.0  # pci


@dataclass
class Plastic3SmoothComponent(PipeGroupComponent["Plastic3SmoothComponent"]):
    linetype_key: ClassVar[CidLineType] = B3PlasticASmooth
    # for ANALYS only
    # WallType = SMOOTH
    height: CandeFloat = 0.0  # in


@dataclass
class Plastic3GeneralComponent(PipeGroupComponent["Plastic3GeneralComponent"]):
    linetype_key: ClassVar[CidLineType] = B3PlasticAGeneral
    # for ANALYS only
    # WallType = GENERAL
    height: CandeFloat = 0.0  # in
    area: CandeFloat = 0.0  # in2/in
    i: CandeFloat = 0.0  # in4/in
    centroid: CandeFloat = 0.0  # in


@dataclass
class Plastic3ProfileComponent(PipeGroupComponent["Plastic3ProfileComponent"]):
    linetype_key: ClassVar[CidLineType] = B3PlasticAProfile
    # for ANALYS only
    # WallType = PROFILE
    # repeatable (multiple properties in one pipe group)
    period: CandeFloat = 0.0  # in
    height: CandeFloat = 0.0  # in
    webangle: CandeFloat = 90.0  # degrees
    webthickness: CandeFloat = 0.0  # in
    webk: CandeFloat = 4.0
    # 0 to 4
    numhorizontal: CandeNum = 0
    # 1: include, -1: ignore
    buckling: CandeNum = 1
    first: CandeNum = 0
    last: CandeNum = 1


@dataclass
class Plastic3bAProfileComponent(PipeGroupComponent["Plastic3bAProfileComponent"]):
    linetype_key: ClassVar[CidLineType] = B3bPlasticAProfile
    # for ANALYS only
    # WallType = PROFILE
    # Required for each NumHorizontal elements in each repeated B3 line
    # 1: inner valley, 2: inner liner, 3: outer crest, 4: outer link
    identifier: CandeNum = 0
    length: CandeFloat = 0.0  # in
    thickness: CandeFloat = 0.0  # in
    supportk: CandeFloat = 4.0


@dataclass
class Plastic3DWSDComponent(PipeGroupComponent["Plastic3DWSDComponent"]):
    linetype_key: ClassVar[CidLineType] = B3PlasticDWSD
    # for DESIGN only
    # WallType = SMOOTH
    # Non LRFD only
    yieldfs: CandeFloat = 2.0
    bucklingfs: CandeFloat = 3.0
    strainfs: CandeFloat = 2.0
    deflection: CandeFloat = 5.0  # percent
    tensile: CandeFloat = 0.05  # in/in


@dataclass
class Plastic3DLRFDComponent(PipeGroupComponent["Plastic3DLRFDComponent"]):
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
class Plastic4DSmoothLRFDComponent(PipeGroupComponent["Plastic4DSmoothLRFDComponent"]):
    linetype_key: ClassVar[CidLineType] = B4Plastic
    # for DESIGN only
    # WallType = SMOOTH
    # LRFD only
    yieldϕ: CandeFloat = 1.0
    bucklingϕ: CandeFloat = 1.0
    strainϕ: CandeFloat = 1.0
    deflectionpercent: CandeFloat = 5.0  # percent
    tensileservice: CandeFloat = 0.05  # in/in
