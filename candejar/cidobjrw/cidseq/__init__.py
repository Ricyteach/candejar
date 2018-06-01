# -*- coding: utf-8 -*-

"""CID sequence module for working with CID sub object sequences (pipe groups, nodes, etc)."""

from ..names import SEQ_TYPES_DICT
from .cidseq import CidSeq, subclass_CidSeq, _COMPLETE
from .cidseqmaterials import SoilMaterialSeq, InterfMaterialSeq

PipeGroupSeq = subclass_CidSeq(SEQ_TYPES_DICT["pipegroups"])
NodeSeq = subclass_CidSeq(SEQ_TYPES_DICT["nodes"])
ElementSeq = subclass_CidSeq(SEQ_TYPES_DICT["elements"])
BoundarySeq = subclass_CidSeq(SEQ_TYPES_DICT["boundaries"])
MaterialSeq = subclass_CidSeq(SEQ_TYPES_DICT["materials"])
FactorSeq = subclass_CidSeq(SEQ_TYPES_DICT["factors"])

__all__ = "PipeGroupSeq NodeSeq ElementSeq BoundarySeq SoilMaterials InterfMaterialSeq MaterialSeq FactorSeq".split()
