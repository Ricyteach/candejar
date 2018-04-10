# -*- coding: utf-8 -*-

"""Module defining CidSeq base object."""
from dataclasses import field, InitVar, make_dataclass, dataclass, asdict
from typing import Sequence, Generic, Type, Iterator, Union, TypeVar, Optional, Counter

from ..cidsubobj import CidSubObj, SUB_OBJ_NAMES_DICT
from ... import fea
from ...cid import CidSubLine
from ...utilities.mixins import ChildRegistryBase
from ..exc import CIDRWError
from .names import TYPE_DICT, SEQ_CLASS_DICT


class CIDSubSeqError(CIDRWError):
    pass


CidObj = TypeVar("CidObj", covariant=True)
SubObj = CidSubObj[CidObj, "CidSeq", CidSubLine, fea.FEAObj]


@dataclass(eq=False)
class CidSeq(ChildRegistryBase, Sequence[SubObj], Generic[CidObj, CidSubLine, fea.FEAObj]):
    cid_obj: InitVar[CidObj]

    def __post_init__(self, cid_obj: CidObj) -> None:
        self.cid_obj = cid_obj
        # make ABC
        if type(self)==CidSeq:
            raise TypeError("Can't instantiate abstract class CidSeq without abstract field line_type")

    @property
    def type_(self) -> Type[fea.FEAObj]:
        fea_type: Type[fea.FEAObj] = TYPE_DICT[self.line_type]
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
            raise CIDSubSeqError(f"Could not locate {self.line_type.__name__!s} object number {num!s}")
        for line in i_line_objs:
            if not isinstance(line, self.line_type):
                yield line
            else:
                break

    def __getitem__(self, val: Union[slice, int]) -> SubObj:
        # TODO: implement slicing
        d = dict()
        for obj in self.iter_sublines(val):
            d.update(asdict(obj))
        try:
            result = CidSubObj.subclasses[SUB_OBJ_NAMES_DICT[self.line_type]](self, **d)
        except CIDSubSeqError as e:
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
    FEA_Obj = TYPE_DICT[sub_line_type]  # type of FEA object corresponding to CID object

    cls = make_dataclass(cls_name, (("line_type", Type[SubLine], field(default=SubLine, init=False, repr=False)),),
                         bases = (CidSeq[CidObj, SubLine, FEA_Obj], Generic[CidObj]), eq=False)

    return cls
