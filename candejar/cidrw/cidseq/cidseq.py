# -*- coding: utf-8 -*-

"""Module defining CidSeq base object."""
from dataclasses import field, InitVar, make_dataclass, dataclass
from typing import Sequence, Generic, Type, Iterator, Union, TypeVar, Optional

from ... import fea
from ...cid import CidSubLine
from ...utilities.mixins import ChildRegistryBase
from ..cidsubobj import CidSubObj
from ..exc import CIDRWError
from .names import SEQ_NAMES, TYPE_DICT, SEQ_CLASS_DICT


class CIDSubSeqError(CIDRWError):
    pass


CidObj = TypeVar("CidObj", covariant=True)
SubObj = CidSubObj[CidObj, "CidSeq", CidSubLine, fea.FEAObj]


@dataclass
class CidSeq(ChildRegistryBase, Sequence[SubObj], Generic[CidObj, CidSubLine, fea.FEAObj]):
    cid_obj: CidObj = field(repr=False)
    seq: Optional[Sequence[SubObj]] = field(default=None, init=False)
    seq_name: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        # make ABC
        if type(self)==CidSeq:
            raise TypeError("Can't instantiate abstract class CidSeq without abstract field line_type")
        self.seq = []

    @property
    def type_(self) -> Type[fea.FEAObj]:
        fea_type: Type[fea.FEAObj] = TYPE_DICT[self.line_type]
        return fea_type

    @property
    def iter_sequence(self) -> Iterator[CidSubLine]:
        yield from (obj for obj in self.cid_obj.line_objs if isinstance(obj, self.line_type))

    def update_seq(self) -> None:
        i_seq =self.iter_sequence
        for i,_ in enumerate(self.seq):
            try:
                next(i_seq)
            except StopIteration:
                raise CIDSubSeqError(f"The CidSeq object [{i}] has no corresponding line object.")
        for _ in i_seq:
            obj = CidSubObj(self, len(self))
            self.add_new(obj)

    def add_new(self, obj: CidSubObj[CidObj, "CidSeq", CidSubLine, fea.FEAObj]) -> None:
        self.seq.append(obj)

    def __getitem__(self, val: Union[slice, int]) -> CidSubObj[CidObj, "CidSeq", CidSubLine, fea.FEAObj]:
        try:
            self.update_seq()
        except CIDSubSeqError:
            raise IndexError(f"{val!s} exceeds available indexes for {self.line_type.__name__} objects")
        result: CidSubObj[CidObj, "CidSeq", CidSubLine, fea.FEAObj] = self.seq[val]
        return result

    def __len__(self) -> int:
        try:
            s = self.seq
        except AttributeError:
            return 0
        else:
            return len(s)


def subclass_CidSeq(sub_line_type):
    """Produce a `CidSeq` based subclass `dataclass`."""

    # see if already exists
    cls_name = SEQ_CLASS_DICT[sub_line_type]
    try:
        return CidSeq.subclasses[cls_name]
    except KeyError:
        pass

    # resolve 3 of the CidSeq input types
    SubLine = sub_line_type  # type of CidLine indicating start of an object in CID file
    FEA_Obj = TYPE_DICT[sub_line_type]  # type of FEA object corresponding to CID object

    cls = make_dataclass(cls_name, (("line_type", Type[SubLine], field(default=SubLine, init=False, repr=False)),),
                         bases = (CidSeq[CidObj, SubLine, FEA_Obj], Generic[CidObj]), eq=False)

    return cls
