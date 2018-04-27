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

