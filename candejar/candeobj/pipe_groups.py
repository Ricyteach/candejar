# -*- coding: utf-8 -*-

"""Module for working with cande pipe group type objects."""

from dataclasses import dataclass
from types import new_class
from typing import Tuple, Callable, ClassVar

from ..cidobjrw.cidsubobj.names import PIPE_GROUP_CLASS_DICT
from ..utilities.mixins import ChildRegistryMixin, ChildRegistryError
from ..cid import A2, B1Basic, B2Basic
from ..cid import CidLineType
from .exc import CandeValueError
from .bases import CandeData
from .keyby import key_by_cid_linetype

#  TODO: PipeGroup objects can contain a wide variety of attributes; need to find a way to accommodate
@dataclass
class PipeGroup(ChildRegistryMixin):
    type_: str  # ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE
    def __new__(cls, type_, *args, **kwargs):
        if cls is PipeGroup:
            pipe_cls = dict(BASIC=Basic, ALUMINUM=Aluminum,
                            STEEL=Steel, PLASTIC=Plastic)[type_]
            return super(PipeGroup,pipe_cls).__new__(pipe_cls)
        else:
            return super(PipeGroup,cls).__new__(cls)


def make_pipe_group(cid, type_: str, **kwargs: CandeData):
    """Make a new pipe group based on contents of the `cid` object and keyword arguments"""
    try:
        cls_name = type_.capitalize()
    except AttributeError:
        raise CandeValueError("Invalid pipe group name type: {type(type_).__name__}")
    try:
        cls = PipeGroup.getsubcls(cls_name)
    except ChildRegistryError:
        raise CandeValueError("Invalid pipe group  name: {type_!r}")
    obj = cls()
    # TODO: finish building pipe group instances using cidprocessing and composite design pattern
    if isinstance(obj, Plastic):
        walltype = kwargs.pop("walltype") # required
        # dispatch to Plastic processing
    elif isinstance(obj, Steel):
        if kwargs.pop("jointslip", None): # optional
            # handle jointslip - add to obj state?
            pass
    elif isinstance(obj, Aluminum):
        # no kwargs to handle
        pass
    elif isinstance(obj, Basic):
        # no kwargs to handle
        pass
    return obj

@dataclass
class Basic(PipeGroup, make_reg_key= lambda subcls: key_by_cid_linetype(Basic)(subcls)):
    line_type: ClassVar[CidLineType] = A2
    type_: str  = "BASIC"
    def __new__(cls, type_: str = "BASIC"):
        return super().__new__(cls, type_)

@dataclass
class Basic1(Basic):
    line_type: ClassVar[CidLineType] = B1Basic
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
class Basic2(Basic1):
    line_type: ClassVar[CidLineType] = B2Basic
    # for ANALYS mode only
    # Small Deformation: 0, Large Deformation: 1, Plus Buckling: 2
    mode: int = 0


@dataclass
class Aluminum(PipeGroup):
    pass


@dataclass
class Steel(PipeGroup):
    pass

# TODO: finish implementing Plastic subclasses
@dataclass
class Plastic(PipeGroup):
    #B1Plastic:
    # GENERAL, SMOOTH, PROFILE
    walltype: float = "GENERAL"
    # HDPE, PVC, PP, OTHER
    pipetype: float = "HDPE"
    # 1: Short term, 2: Long term
    duration: int = 1
    # Small Deformation: 0, Large Deformation: 1, Plus Buckling: 2
    mode: int = 0
    #B2Plastic:
    shortmodulus: float = 0.0 # psi
    shortstrength: float = 0.0 # psi
    longmodulus: float = 0.0 # psi
    longstrength: float = 0.0 # psi
    poissons: float = 0.3
    density: float = 0.0 # pci

@dataclass
class PlasticSmooth(Plastic):
    #B3PlasticASmooth:
    # for ANALYS only
    # WallType = SMOOTH
    height: float = 0.0 # in

@dataclass
class PlasticGeneral(Plastic):
    #B3PlasticAGeneral:
    # for ANALYS only
    # WallType = GENERAL
    height: float = 0.0 # in
    area: float = 0.0 # in2/in
    i: float = 0.0 # in4/in
    centroid: float = 0.0 # in

@dataclass
class PlasticProfile(Plastic):
    #B3PlasticAProfile:
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
    #B3bPlasticAProfile:
    # for ANALYS only
    # WallType = PROFILE
    # Required for each NumHorizontal elements in each repeated B3 line
    # 1: inner valley, 2: inner liner, 3: outer crest, 4: outer link
    identifier: int = 0
    length: float = 0.0 # in
    thickness: float = 0.0 # in
    supportk: float = 4.0
    #B3PlasticDWSD:
    # for DESIGN only
    # WallType = SMOOTH
    # Non LRFD only
    yieldfs: float = 2.0
    bucklingfs: float = 3.0
    strainfs: float = 2.0
    deflection: float = 5.0 # percent
    tensile: float = 0.05 # in/in
    #B3PlasticDLRFD:
    # for DESIGN only
    # WallType = SMOOTH
    # LRFD only
    yield_: float = 1.0
    buckling: float = 1.0
    strain: float = 1.0
    deflection: float = 1.0
    tensile: float = 1.0
    #B4Plastic:
    # for DESIGN only
    # WallType = SMOOTH
    # LRFD only
    yieldϕ: float = 1.0
    bucklingϕ: float = 1.0
    strainϕ: float = 1.0
    deflectionpercent: float = 5.0 # percent
    tensileservice: float = 0.05 # in/in


def subclass_PipeGroupObj(type_):
    """Produce a `PipeGroup` based subclass."""

    # see if already exists
    pipe_group_cls_name = PIPE_GROUP_CLASS_DICT[type_]
    try:
        return PipeGroup.getsubcls(pipe_group_cls_name)
    except ChildRegistryError:
        pass

    cls = new_class(pipe_group_cls_name, (PipeGroup,))

    return cls
