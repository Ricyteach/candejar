# -*- coding: utf-8 -*-

"""Module for working with cande pipe group type objects."""

from types import new_class

from ..cidprocessing.L3 import PipeGroup as process_pipegroup
# from ..cidobjrw.cidsubobj.names import PIPE_GROUP_CLASS_DICT
from ..utilities.mixins import ChildRegistryError
from .exc import CandeValueError
from .bases import CandeData, CandeComposite
# from .keyby import key_by_cid_linetype

# TODO: Implement PipeGroup type_ dispatching
class PipeGroup(CandeComposite):
    pass

class Basic(PipeGroup):
    pass

class Aluminum(PipeGroup):
    pass

class Steel(PipeGroup):
    pass

# TODO: Implement Plastic walltype dispatching
class Plastic(PipeGroup):
    pass

def make_pipe_group(cid, type_: str, **kwargs: CandeData):
    """Make a new pipe group

    The arguments are dispatched to the appropriate `PipeGroup` subclass
    based on contents of the `cid` object and keyword arguments
    """
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
    type_gen = process_pipegroup(cid, group_num, obj)
    keys = tuple(type_gen)
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
