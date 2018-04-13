# -*- coding: utf-8 -*-

"""Module defining CidSeq base object."""
import types
from dataclasses import InitVar, dataclass, asdict
from typing import Sequence, Generic, Type, Iterator, Union, TypeVar, Counter, MutableMapping, MutableSequence, Mapping

from ... import fea
from ...cid import CidSubLine, TOP_LEVEL_TYPES
from ...utilities.mixins import ChildRegistryBase
from ...utilities.dataclasses import shallow_mapify
from ..cidsubobj import CidSubObj, SUB_OBJ_NAMES_DICT
from ..exc import CIDObjError
from ..cidsubobj.cidsubobj import CidData
from ..names import FEA_TYPE_DICT
from .names import SEQ_CLASS_DICT


class CIDSubSeqIndexError(CIDObjError, IndexError):
    pass


CidObj = TypeVar("CidObj", covariant=True)
SubObj = CidSubObj[CidObj, "CidSeq", CidSubLine, fea.FEAObj]


@dataclass(eq=False)
class CidSeq(ChildRegistryBase, Sequence[SubObj], Generic[CidObj, CidSubLine, fea.FEAObj]):
    cid_obj: InitVar[CidObj]

    def __post_init__(self, cid_obj: CidObj) -> None:
        self.cid_obj = cid_obj
        # make ABC
        if type(self)==CidSeq or self.line_type==NotImplemented:
            raise TypeError("Can't instantiate abstract class CidSeq without abstract class attribute line_type")

    @property
    def line_type(self):
        return NotImplemented

    @property
    def type_(self) -> Type[fea.FEAObj]:
        fea_type: Type[fea.FEAObj] = FEA_TYPE_DICT[self.line_type]
        return fea_type

    @property
    def iter_main_lines(self) -> Iterator[CidSubLine]:
        """Iterate the line objects associated with the container line_type"""
        yield from (obj for obj in self.cid_obj.line_objs if isinstance(obj, self.line_type))

    def iter_sublines(self, idx) -> Iterator[CidSubLine]:
        """Iterate the line objects associated with the provided index"""
        # TODO: implement slicing
        i_line_objs = iter(self.cid_obj.line_objs)
        num = idx + 1
        start_ctr = Counter()
        for line in i_line_objs:
            start_ctr[isinstance(line, self.line_type)] += 1
            if start_ctr[True] == num:
                yield line
                break
        else:
            raise CIDSubSeqIndexError(f"Could not locate {self.line_type.__name__!s} object number {num!s}")
        for line in i_line_objs:
            if type(line) in TOP_LEVEL_TYPES:
                break
            else:
                yield line

    def _asdict(self) -> MutableSequence[Mapping[str,CidData]]:
        return [shallow_mapify(i) for i in self]

    def __getitem__(self, val: Union[slice, int]) -> SubObj:
        # TODO: implement slicing
        d = dict()
        for obj in self.iter_sublines(val):
            d.update(asdict(obj))
        try:
            result = CidSubObj.subclasses[SUB_OBJ_NAMES_DICT[self.line_type]](self, val, **d)
        except CIDSubSeqIndexError as e:
            raise IndexError(f"{val!s} not an available index for {self.line_type.__name__} object") from e
        return result

    def __len__(self) -> int:
        return sum(1 for _ in self.iter_main_lines)


def subclass_CidSeq(sub_line_type):
    """Produce a `CidSeq` based subclass `dataclass`."""

    # see if already exists
    cls_name = SEQ_CLASS_DICT[sub_line_type]
    try:
        return CidSeq.subclasses[cls_name]
    except KeyError:
        pass

    # resolve 2 of the CidSeq input types
    SubLine = sub_line_type  # type of CidLine indicating start of an object in CID file
    FEA_Obj = FEA_TYPE_DICT[sub_line_type]  # type of FEA object corresponding to CID object

    cls = types.new_class(cls_name, (CidSeq[CidObj, SubLine, FEA_Obj], Generic[CidObj]), exec_body=lambda ns: ns.update(dict(line_type=SubLine)))

    return cls
