# -*- coding: utf-8 -*-

"""Module defining CidSeq base object."""
import types
from dataclasses import InitVar, dataclass, asdict
from itertools import count
from typing import Sequence, Generic, Type, Iterator, Union, TypeVar, Counter, List, Dict

from ...cid import CidLine
from ... import fea
from ...cid import CidSubLine, TOP_LEVEL_TYPES
from ...utilities.mixins import ChildRegistryBase
from ...utilities.dataclasses import shallow_mapify
from ..cidsubobj import CidSubObj, SUB_OBJ_NAMES_DICT
from ..cidsubobj.cidsubobj import CidData
from ..names import FEA_TYPE_DICT, SEQ_LINE_TYPE_TOTAL_DICT
from .names import SEQ_CLASS_DICT
from .exc import CIDSubSeqIndexError

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

    def _asdict(self) -> List[Dict[str,CidData]]:
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

    def __iter__(self):
        total_attr_name = SEQ_LINE_TYPE_TOTAL_DICT[self.line_type]
        seq_total = getattr(self.cid_obj, total_attr_name)
        if seq_total:
            yield from (CidSubObj.subclasses[SUB_OBJ_NAMES_DICT[self.line_type]](self, x) for x in count())

    def __len__(self) -> int:
        return sum(1 for _ in self.iter_main_lines)


def subclass_CidSeq(sub_line_type: Type[CidLine]) -> Type[CidSeq]:
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

    cls: Type[CidSeq] = types.new_class(cls_name, (CidSeq[CidObj, SubLine, FEA_Obj], Generic[CidObj]), exec_body=lambda ns: ns.update(dict(line_type=SubLine)))

    return cls
