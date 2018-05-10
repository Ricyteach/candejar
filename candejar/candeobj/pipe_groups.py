# -*- coding: utf-8 -*-

"""Module for working with cande pipe group type objects."""

from dataclasses import fields, dataclass, InitVar
from enum import Enum
from typing import Union

from ..utilities.mixins import child_dispatcher
from ..utilities.enumtools import CapitalizedEnumMixin, callable_enum_dispatcher
from ..utilities.decorators import case_insensitive_arguments
from ..cidprocessing.L3 import PipeGroup as process_PipeGroup
from .pipe_group_components import PipeGroupComponent
from .exc import CandeValueError
from .bases import CandeData, CandeComposite, CandeStr

# the type_: InitVar[CandeStr] fields below are used by the PipeGroup __new__ constructor
# for dispatching to its child classes; no __post_init__ handling is needed

@child_dispatcher("type_")
@dataclass(eq=False)
class PipeGroup(CandeComposite):
    type_: InitVar[CandeStr]
    def __post_init__(self, type_: CandeStr):
        CandeComposite.__init__(self)

@case_insensitive_arguments
@callable_enum_dispatcher(dispatch_func=PipeGroup.getsubcls)
class PipeType(CapitalizedEnumMixin):
    BASIC="Basic"
    ALUMINUM="Aluminum"
    STEEL="Steel"
    PLASTIC="Plastic"

@dataclass
class Basic(PipeGroup):
    type_: InitVar[CandeStr] = "BASIC"

@dataclass
class Aluminum(PipeGroup):
    type_: InitVar[CandeStr] = "ALUMINUM"

@dataclass
class Steel(PipeGroup):
    type_: InitVar[CandeStr] = "STEEL"

# TODO: Implement Plastic walltype dispatching
@dataclass
class Plastic(PipeGroup):
    type_: InitVar[CandeStr] = "PLASTIC"

@case_insensitive_arguments
@callable_enum_dispatcher(dispatch_func=Plastic.getsubcls)
class PlasticType(Enum):
    GENERAL="GENERAL"
    SMOOTH="SMOOTH"
    PROFILE="PROFILE"

# TODO: Implement Concrete pipe material pipe groups (Concrete, Conrib, Contube)

def make_pipe_group(cid, type_: Union[str, PipeType, PlasticType], **kwargs: CandeData):
    """Make a new pipe group

    The arguments are dispatched to the appropriate `PipeGroup` subclass
    based on contents of the `cid` object and keyword arguments
    """
    try:
        type_ = PipeType(type_).value
    except ValueError as e:
        if isinstance(type_,PlasticType):
            type_ = PipeType.PLASTIC.value
            walltype = PlasticType(type_).value
            if kwargs.get("walltype","") != walltype:
                raise CandeValueError(f"conflicting plastic walltypes detected: {kwargs['walltype']!r} and {walltype!r}")
            else:
                kwargs.update(walltype=walltype)
        else:
            raise e
    finally:
        kwargs.update(type_=type_)
    pipe_group = PipeGroup(type_)
    if isinstance(pipe_group, Plastic):
        if "walltype" not in kwargs:
            # required for dispatching to correct plastic subclass
            raise CandeValueError("'walltype' argument is required for Plastic pipe types")
        # TODO: handle multiple B3PlasticAProfile and B3bPlasticAProfile components
    elif isinstance(pipe_group, Steel):
        if "jointslip" not in kwargs:
            # TODO: decide whether to add jointslip to pipe_group state if missing
            pass
    elif isinstance(pipe_group, Basic):
        # TODO: handle multiple B1Basic components
        pass
    # TODO: handle various concrete components/types
    group_num = len(getattr(pipe_group,"pipe_groups",[]))+1
    iter_linetype = process_PipeGroup(cid, group_num, pipe_group)
    for linetype in iter_linetype:
        ComponentCls = PipeGroupComponent.getsubcls(linetype)
        field_names = [f.name for f in fields(ComponentCls)]
        cls_kwargs={k:kwargs.pop(k) for k in kwargs.copy().keys() if k in field_names}
        pipe_group_component=ComponentCls(**cls_kwargs)
        pipe_group.add_component(pipe_group_component)
        del ComponentCls
    if kwargs:
        raise CandeValueError(f"Unusable arguments values were provided: {str(kwargs)[1:-1]}")
    return pipe_group
