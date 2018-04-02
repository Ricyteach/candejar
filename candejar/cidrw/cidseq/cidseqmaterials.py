from dataclasses import dataclass, field, InitVar
from typing import TypeVar, Type, Optional, Sequence, Generic, Iterator

from ... import fea
from ...cid import D1
from ..cidsubobj import CidSubObj
from .cidseq import CidSeq

CidObj = TypeVar("CidObj", covariant=True)
SoilMatObj = CidSubObj[CidObj, "SoilMaterials", D1, fea.Material]
InterfMatObj = CidSubObj[CidObj, "InterfMaterials", D1, fea.Material]


@dataclass
class SoilMaterials(CidSeq[CidObj, D1, fea.Material], Generic[CidObj]):
    line_type: Type[D1] = field(default=D1, init=False, repr=False)

    @property
    def iter_sequence(self) -> Iterator[D1]:
        """Alternate line sequence iterator for soil materials (all types but 6,7)"""
        yield from (i for i in super().iter_sequence if getattr(i,"model",None) not in (6,7,None))


@dataclass
class InterfMaterials(CidSeq[CidObj, D1, fea.Material], Generic[CidObj]):
    line_type: Type[D1] = field(default=D1, init=False, repr=False)

    @property
    def iter_sequence_interfmaterial(self) -> Iterator[D1]:
        """Alternate line sequence iterator for interface materials (type 6 only)"""
        yield from (i for i in super().iter_sequence if getattr(i,"model",None)==6)
