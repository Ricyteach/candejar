# -*- coding: utf-8 -*-

"""CID sub objectmodule for working with CID sub objects (pipe grous, node, etc)."""
from ..names import SEQ_NAMES_DICT
from .names import SEQ_LINE_TYPES, SUB_OBJ_CLASS_NAMES
from .cidsubobj import subclass_CidSubObj, CidSubObj

PipeGroup = subclass_CidSubObj(SEQ_NAMES_DICT["pipe_groups"])
Node = subclass_CidSubObj(SEQ_NAMES_DICT["nodes"])
Element = subclass_CidSubObj(SEQ_NAMES_DICT["elements"])
Boundary = subclass_CidSubObj(SEQ_NAMES_DICT["boundaries"])
Material = subclass_CidSubObj(SEQ_NAMES_DICT["materials"])
Factor = subclass_CidSubObj(SEQ_NAMES_DICT["factors"])

SUB_OBJ_DICT = dict(zip(SEQ_LINE_TYPES, (PipeGroup, Node, Element, Boundary, Material, Factor)))
SUB_OBJ_NAMES_DICT = dict(zip(SEQ_LINE_TYPES, SUB_OBJ_CLASS_NAMES))

__all__ = SUB_OBJ_CLASS_NAMES

def __dir__():
    return __all__ + (CidSubObj, SUB_OBJ_DICT)
