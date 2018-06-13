# -*- coding: utf-8 -*-

"""Module defining CidSeq objects for soil materials and interface materials."""

# TODO: Add link element materials

from typing import TypeVar, Generic, Iterator, Counter

from ...cid import CidSubLine, D1
from ..cidsubobj import CidSubObj, SUB_OBJ_NAMES_DICT
from .cidseq import CidSeq, SubObj
from .exc import CIDSubSeqIndexError

CidObj = TypeVar("CidObj", covariant=True)
SoilMatObj = CidSubObj[CidObj, "SoilMaterialSeq", D1]
InterfMatObj = CidSubObj[CidObj, "InterfMaterialSeq", D1]


class SoilMaterialSeq(CidSeq[CidObj, D1], Generic[CidObj]):
    line_type = D1

    @property
    def iter_main_lines(self) -> Iterator[D1]:
        """Alternate line sequence iterator for soil materials (all types but 6,7)"""
        yield from (i for i in super().iter_main_lines if getattr(i, "model", None) not in (6, 7, None))

    def iter_sublines(self, idx) -> Iterator[CidSubLine]:
        """Iterate only the soil material line objects associated with the provided index"""
        # TODO: implement slicing
        ctr = Counter()
        for D1_idx, main_line_candidate in enumerate(super().iter_main_lines):
            if main_line_candidate.model!=6 and ctr[main_line_candidate.model!=6] == idx:
                yield from super().iter_sublines(D1_idx)
                break
            ctr[main_line_candidate.model!=6] += 1
        else:
            num = idx+1
            raise CIDSubSeqIndexError(f"Could not locate {self.line_type.__name__!s} soil object number {num!s}")

    def iter_init(self) -> Iterator[SubObj]:
        """Extends CidSeq.iter_init so that the soil material count is utilized."""
        # get the associated total item count
        seq_total = getattr(self.cid_obj, "nsoilmaterials")
        # get the sub-object type
        SubObjCls: Type[SubObj] = CidSubObj.getsubcls(SUB_OBJ_NAMES_DICT[self.line_type])[CidObj, CidSeq]
        # produce items up to the specified item total
        for x in range(seq_total):
            subobj = SubObjCls(self, x)
            yield subobj

    def __len__(self) -> int:
        return sum(1 for line in self.iter_main_lines if line.model!=6)


class InterfMaterialSeq(CidSeq[CidObj, D1], Generic[CidObj]):
    line_type = D1

    @property
    def iter_main_lines(self) -> Iterator[D1]:
        """Line sequence iterator for interface materials (type 6 only)"""
        yield from (i for i in super().iter_main_lines if getattr(i, "model", None) == 6)

    def iter_sublines(self, idx) -> Iterator[CidSubLine]:
        """Iterate only the interface material line objects associated with the provided index"""
        # TODO: implement slicing
        ctr = Counter()
        for D1_idx, main_line_candidate in enumerate(super().iter_main_lines):
            if main_line_candidate.model==6 and ctr[main_line_candidate.model==6] == idx:
                yield from super().iter_sublines(D1_idx)
                break
            ctr[main_line_candidate.model==6] += 1
        else:
            num = idx+1
            raise CIDSubSeqIndexError(f"Could not locate {self.line_type.__name__!s} interface object number {num!s}")

    def iter_init(self) -> Iterator[SubObj]:
        """Extends CidSeq.iter_init so that the interface material count is utilized."""
        # get the associated total item count
        seq_total = getattr(self.cid_obj, "ninterfmaterials")
        # get the sub-object type
        SubObjCls: Type[SubObj] = CidSubObj.getsubcls(SUB_OBJ_NAMES_DICT[self.line_type])[CidObj, CidSeq]
        # produce items up to the specified item total
        for x in range(seq_total):
            subobj = SubObjCls(self, x)
            yield subobj

    def __len__(self) -> int:
        return sum(1 for line in self.iter_main_lines if line.model==6)
