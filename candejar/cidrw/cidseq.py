# -*- coding: utf-8 -*-

"""CID sequence module for working with CID sub object sequences (pipe groups, nodes, etc)."""
from abc import abstractmethod
from dataclasses import field, InitVar, make_dataclass
from typing import Sequence, Generic, Type, Iterator, Union, TypeVar, Optional

from .. import fea
from ..cid import CidSubLine
from ..utilities.mixins import ChildRegistryBase
from .cidsubobj import CidSubObj
from .exc import CIDRWError
from . import SEQ_NAME_DICT, TYPE_DICT, SEQ_CLASS_DICT


class CIDSubSeqError(CIDRWError):
    pass


CidObj = TypeVar("CidObj", covariant=True)


class CidSeq(ChildRegistryBase, Sequence[CidSubObj[CidObj, "CidSeq", CidSubLine, fea.FEAObj]], Generic[CidObj, CidSubLine, fea.FEAObj]):

    def __post_init__(self, seq_name: str) -> None:
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
            obj = CidSubObj(self, len(self))
            self.add_new(obj)

    @abstractmethod
    def add_new(self, obj: CidSubObj[CidObj, "CidSeq", CidSubLine, fea.FEAObj]) -> None: ...

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


def subclass_CidSeq(seq_name):
    """Produce a `CidSeq` based subclass `dataclass`."""

    # see if already exists
    cls_name = SEQ_CLASS_DICT[seq_name]
    try:
        return CidSeq.subclasses[cls_name]
    except KeyError:
        pass

    # resolve all the types
    SubLine = SEQ_NAME_DICT[seq_name]  # type of CidLine indicating start of an object in CID file
    FEA_Obj = TYPE_DICT[SEQ_NAME_DICT[seq_name]]  # type of FEA object corresponding to CID object
    CidSeqChild = CidSeq[CidObj, SubLine, FEA_Obj]
    SubObj = CidSubObj[CidObj, CidSeqChild, SubLine, FEA_Obj]

    # provide alternate new object insertion for soil materials (needs to be insert into middle
    # of the `ChainSequence` container).
    def add_new_soilmaterial(self, material: SubObj) -> None:
        self.seq.sequences[0].append(material)

    # default new object insertion for all other `CidSeq` children
    def add_new_(self, item: SubObj) -> None:
        self.seq.append(item)

    # lookup correct `add_new` method
    add_new_dict = dict(soilmaterials=add_new_soilmaterial)
    add_new_method = add_new_dict.get(seq_name, add_new_)

    # TODO: this will not work as-is because `make_dataclass` calls `type` with the namespace instead of `types.new_class`
    # Changing to `types.new_class` creates a new problem because `make_dataclass` doesn't know to utilize exec_body

    cls = make_dataclass(cls_name,
                         (("cid_obj", CidObj, field(repr=False)),
                          ("seq_name", InitVar[str]),
                          ("line_type", Type[SubLine], field(default=SubLine, init=False, repr=False)),
                          ("seq", Optional[Sequence[SubObj]], field(default=None, init=False))),
                         bases = (CidSeqChild, Generic[CidObj]),
                         namespace = dict(), eq=False)

    return cls
