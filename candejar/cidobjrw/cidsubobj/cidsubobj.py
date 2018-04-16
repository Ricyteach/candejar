# -*- coding: utf-8 -*-

"""A viewer for a CID sub object (pipe group, node, etc) using a `SimpleNamespace` instance returned on the fly."""
from types import new_class
from typing import Generic, Union, TypeVar, Dict

from ..names import FEA_TYPE_DICT
from .names import SUB_OBJ_CLASS_DICT
from ...utilities.mixins import ChildRegistryBase
from ...cid import CidSubLine
from ... import fea


# The `SimpleNamespace` is just a current view of the combined attributes from the relevant file `CidLine`s.
# Is created on the fly by the containing `CidSeq`


CidData = Union[int, float, str, None]
CidObj = TypeVar("CidObj")
CidSeq = TypeVar("CidSeq")


class CidSubObj(ChildRegistryBase, Generic[CidObj, CidSeq, CidSubLine, fea.FEAObj]):
    """A viewer object that gets its data from the `CidLine` objects in `.cid_obj`."""

    def __init__(self, _container: CidSeq, _idx: int, **kwargs: CidData):
        # make ABC
        if type(self)==CidSubObj:
            raise TypeError("Can't instantiate abstract class CidSubObj without line_type attribute")
        self._container = _container
        self._idx = _idx
        self.__dict__.update(kwargs)

    def _asdict(self) -> Dict[str, CidData]:
        return {k:v for k,v in vars(self).items() if k not in "_container _idx".split()}

    def __repr__(self):
        items = ("{}={!r}".format(k, v) for k,v in vars(self).items() if k not in "_container _idx".split())
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__repr__() == other.__repr__()

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            new_obj = self._container[self._idx]
            d = self.__dict__ = new_obj.__dict__
            try:
                return d[name]
            except KeyError:
                pass
            raise e

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
    FEA_Obj = FEA_TYPE_DICT[sub_line_type]  # type of FEA object corresponding to CID object

    cls = new_class(cls_name, (CidSubObj[CidObj, CidSeq, SubLine, FEA_Obj], Generic[CidObj, CidSeq]))

    return cls
