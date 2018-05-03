# -*- coding: utf-8 -*-

"""Module for working with cande pipe group type objects."""
from dataclasses import fields
# from types import new_class
from enum import Enum
from typing import Iterator

# from ..cidobjrw.cidsubobj.names import PIPE_GROUP_CLASS_DICT
from ..utilities.mixins import ChildRegistryError, ChildRegistryMixin, child_dispatcher
from ..cid import CidLineType
from .pipe_group_components import PipeGroupComponent
from .exc import CandeValueError
from .bases import CandeData, CandeComposite

class PipeType(Enum):
    basic="Basic"
    aluminum="Aluminum"
    steel="Steel"
    plastic="Plastic"

# TODO: Implement PipeGroup type_ dispatching
@child_dispatcher("type_")
class PipeGroup(ChildRegistryMixin, CandeComposite):
    type_: PipeType

class Basic(PipeGroup):
    pass

class Aluminum(PipeGroup):
    pass

class Steel(PipeGroup):
    pass

# TODO: Implement Plastic walltype dispatching
class Plastic(PipeGroup):
    pass

def make_pipe_group(cid, iter_linetype: Iterator[CidLineType], **kwargs: CandeData):
    """Make a new pipe group

    The arguments are dispatched to the appropriate `PipeGroup` subclass
    based on contents of the `cid` object and keyword arguments
    """
    for linetype in iter_linetype:
        Cls=PipeGroupComponent.getsubcls(linetype)
        cls_kwargs={k:v for k,v in kwargs.items() if k in fields(Cls)}
        pipe_group_component=Cls(cls_kwargs)
        while True:
            try:
                pipe_group.add_component(pipe_group_component)
                break
            except NameError:
                pipe_group = PipeGroup()
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
