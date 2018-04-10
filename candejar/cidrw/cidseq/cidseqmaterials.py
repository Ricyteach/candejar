from typing import TypeVar, Generic, Iterator, Counter

from ... import fea
from ...cid import CidSubLine, D1
from ..cidsubobj import CidSubObj
from .cidseq import CidSeq, CIDSubSeqError

CidObj = TypeVar("CidObj", covariant=True)
SoilMatObj = CidSubObj[CidObj, "SoilMaterials", D1, fea.Material]
InterfMatObj = CidSubObj[CidObj, "InterfMaterials", D1, fea.Material]


class SoilMaterials(CidSeq[CidObj, D1, fea.Material], Generic[CidObj]):
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
            raise CIDSubSeqError(f"Could not locate {self.line_type.__name__!s} soil object number {num!s}")

class InterfMaterials(CidSeq[CidObj, D1, fea.Material], Generic[CidObj]):
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
            raise CIDSubSeqError(f"Could not locate {self.line_type.__name__!s} interface object number {num!s}")
