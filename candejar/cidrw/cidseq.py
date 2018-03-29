# -*- coding: utf-8 -*-

"""CID sequence module for working with CID sub object sequences (pipe groups, nodes, etc)."""

from dataclasses import dataclass, field, InitVar
from typing import Sequence, Generic, Type, MutableSequence, Iterator, Union, TypeVar

from .. import fea
from ..cid import CidSubLine
from .cidsubobj import CidSubObj
from .exc import CIDRWError
from . import SEQ_NAME_DICT, TYPE_DICT


class CIDSubSeqError(CIDRWError):
    pass


CidObj = TypeVar("CidObj")


@dataclass(eq=False)
class CidSeq(Sequence[CidSubObj[CidObj, CidSubLine, fea.FEAObj]], Generic[CidObj, CidSubLine, fea.FEAObj]):
    cid_obj: CidObj = field(repr=False)
    line_type: Type[CidSubLine] = field(init=False, repr=False)
    seq: MutableSequence[CidSubObj[CidObj, CidSubLine, fea.FEAObj]] = field(init=False)
    seq_name: InitVar[str]
    def __post_init__(self, seq_name: str) -> None:
        self.line_type = SEQ_NAME_DICT[seq_name]
        if getattr(self.cid_obj, seq_name):
            self.seq = getattr(self.cid_obj, seq_name)
            if any(not issubclass(obj.fea_obj, self.type_) for obj in self.seq):
                i, c = next(enumerate(o for o in self.seq if not issubclass(o.fea_obj, self.type_)))
                raise CIDRWError(f"The class ({c.__name__}) of item seq[{i}] is not a {self.type_.__name__} subclass.")
        else:
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
            self.add_new()

    def add_new(self) -> None:
        obj = CidSubObj(self, len(self))
        self.seq.append(obj)

    def __getitem__(self, val: Union[slice, int]) -> CidSubObj[CidObj, CidSubLine, fea.FEAObj]:
        try:
            self.update_seq()
        except CIDSubSeqError:
            raise IndexError(f"{val!s} exceeds available indexes for {self.line_type.__name__} objects")
        result: CidSubObj[CidObj, CidSubLine, fea.FEAObj] = self.seq[val]
        return result

    def __len__(self) -> int:
        try:
            s = self.seq
        except AttributeError:
            return 0
        else:
            return len(s)
