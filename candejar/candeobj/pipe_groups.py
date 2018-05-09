# -*- coding: utf-8 -*-

"""Module for working with cande pipe group type objects."""

from dataclasses import fields, dataclass, InitVar, field
# from types import new_class
from enum import Enum
from typing import Iterator, Type

# from ..cidobjrw.cidsubobj.names import PIPE_GROUP_CLASS_DICT
from ..utilities.mixins import ChildRegistryError, child_dispatcher
from ..utilities.enumtools import CapitalizedEnumMixin, callable_enum_dispatcher
from ..utilities.decorators import case_insensitive_arguments
from ..cid import CidLineType
from ..cidprocessing.L3 import PipeGroup as process_PipeGroup
from .pipe_group_components import PipeGroupComponent
from .exc import CandeValueError
from .bases import CandeData, CandeComposite, CandeComponent, CandeStr, CandeNum

# TODO: Implement PipeGroup type_ dispatching
@child_dispatcher("type_")
@dataclass(eq=False)
class PipeGroup(CandeComposite):
    type_: CandeStr = field(default="PLASTIC", repr=False)
    num: CandeNum = 0

@case_insensitive_arguments()
@callable_enum_dispatcher(dispatch_func=PipeGroup.getsubcls)
class PipeType(CapitalizedEnumMixin):
    BASIC="Basic"
    ALUMINUM="Aluminum"
    STEEL="Steel"
    PLASTIC="Plastic"

@dataclass
class Basic(PipeGroup):
    type_: CandeStr = field(default="BASIC", repr=False)

@dataclass
class Aluminum(PipeGroup):
    type_: CandeStr = field(default="ALUMINUM", repr=False)

@dataclass
class Steel(PipeGroup):
    type_: CandeStr = field(default="STEEL", repr=False)

# TODO: Implement Plastic walltype dispatching
@dataclass
class Plastic(PipeGroup):
    type_: CandeStr = field(default="PLASTIC", repr=False)

@case_insensitive_arguments()
@callable_enum_dispatcher(dispatch_func=Plastic.getsubcls)
class PlasticType(Enum):
    GENERAL="GENERAL"
    SMOOTH="SMOOTH"
    PROFILE="PROFILE"

# TODO: Implement Concrete pipe material pipe groups (Concrete, Conrib, Contube)

def make_pipe_group(cid, **kwargs: CandeData):
    """Make a new pipe group

    The arguments are dispatched to the appropriate `PipeGroup` subclass
    based on contents of the `cid` object and keyword arguments
    """
    pipe_group = PipeGroup(kwargs.pop("type_"), kwargs.pop("num",0))
    group_num = len(getattr(pipe_group,"pipe_groups",[]))+1
    iter_linetype = process_PipeGroup(cid, group_num, pipe_group)
    for linetype in iter_linetype:
        ComponentCls: Type[CandeComponent] = PipeGroupComponent.getsubcls(linetype)
        field_names = [f.name for f in fields(ComponentCls)]
        cls_kwargs={k:kwargs.pop(k) for k in kwargs.copy().keys() if k in field_names}
        pipe_group_component=ComponentCls(**cls_kwargs)
        pipe_group.add_component(pipe_group_component)
        del ComponentCls
    return pipe_group
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
        try:
            walltype = kwargs.pop("walltype") # required
        except KeyError:
            raise CandeValueError("'walltype' argument is required for Plastic"
                                  "pipe types")
        # dispatch to Plastic processing
    elif isinstance(obj, Steel):
        if kwargs.pop("jointslip", None): # optional
            # handle jointslip - add to obj state?
            pass
        # dispatch to Steel processing
    elif isinstance(obj, Aluminum):
        # no kwargs to handle
        pass
        # dispatch to Aluminum processing
    elif isinstance(obj, Basic):
        # no kwargs to handle
        pass
        # dispatch to Basic processing
    group_num = len(cid.pipe_groups)+1
    return obj

'''
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
'''
