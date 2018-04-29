# -*- coding: utf-8 -*-

"""Module for working with cande pipe group type objects."""

from dataclasses import dataclass
from types import new_class

from ..cidobjrw.cidsubobj.names import PIPE_GROUP_CLASS_DICT
from ..utilities.mixins import ChildRegistryBase


#  TODO: PipeGroup objects can contain a wide variety of attributes; need to find a way to accommodate
@dataclass
class PipeGroup(ChildRegistryBase):
    type_: str  # ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE
    def __new__(cls, type_, *args, **kwargs):
        if cls is PipeGroup:
            pipe_cls = dict(BASIC=Basic, ALUMINUM=Aluminum,
                            STEEL=Steel, PLASTIC=Plastic)[type_]
            return super(PipeGroup,pipe_cls).__new__(pipe_cls)
        else:
            return super(PipeGroup,cls).__new__(cls)

@dataclass
class Basic(PipeGroup):
    # B1Basic
    # ANALYS only
    # repeatable (multiple properties in one pipe group)
    first: int = 0
    last: int = 0
    modulus: float = 0.0 # psi
    poissons: float = 0.0
    area: float = 0.0 # in2/in
    i: float = 0.0 # in4/in
    load: float = 0.0 # lbs/in

    # B2Basic
    # for ANALYS mode only
    # Small Deformation: 0, Large Deformation: 1, Plus Buckling: 2
    mode: int = 0


@dataclass
class Aluminum(PipeGroup):
    pass


@dataclass
class Steel(PipeGroup):
    pass


@dataclass
class Plastic(PipeGroup):
    pass


def subclass_PipeGroupObj(type_):
    """Produce a `PipeGroup` based subclass."""

    # see if already exists
    pipe_group_cls_name = PIPE_GROUP_CLASS_DICT[type_]
    try:
        return PipeGroup.subclasses[pipe_group_cls_name]
    except KeyError:
        pass

    cls = new_class(pipe_group_cls_name, (PipeGroup,))

    return cls
