# -*- coding: utf-8 -*-

"""A viewer for a CID sub object (pipe group, node, etc) using a `SimpleNamespace` instance returned on the fly."""
from types import SimpleNamespace, new_class
from typing import Generic, Union, TypeVar

from .names import SUB_OBJ_CLASS_DICT, TYPE_DICT
from ...utilities.mixins import ChildRegistryBase
from ...cid import CidSubLine
from ... import fea


# The `SimpleNamespace` is just a current view of the combined attributes from the relevant file `CidLine`s.
# Is created on the fly by the containing `CidSeq`


CidData = Union[int, float, str, None]
CidObj = TypeVar("CidObj")
CidSeq = TypeVar("CidSeq")


class CidSubObj(ChildRegistryBase, SimpleNamespace, Generic[CidObj, CidSeq, CidSubLine, fea.FEAObj]):
    """A viewer object that gets its data from the `CidLine` objects in `.cid_obj`."""

    def __init__(self, container: CidSeq, **kwargs: CidData):
        # make ABC
        if type(self)==CidSubObj:
            raise TypeError("Can't instantiate abstract class CidSubObj without line_type attribute")
        self.container = container
        super().__init__(**kwargs)


def subclass_CidSubObj(sub_line_type):
    """Produce a `CidSubObj` based subclass."""

    # see if already exists
    cls_name = SUB_OBJ_CLASS_DICT[sub_line_type]
    try:
        return CidSubObj.subclasses[cls_name]
    except KeyError:
        pass

    # resolve 2 of the CidSubObj input types
    SubLine = sub_line_type  # type of CidLine indicating start of an object in CID file
    FEA_Obj = TYPE_DICT[sub_line_type]  # type of FEA object corresponding to CID object

    cls = new_class(cls_name, (CidSubObj[CidObj, CidSeq, SubLine, FEA_Obj], Generic[CidObj, CidSeq]))

    return cls
