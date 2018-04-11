# -*- coding: utf-8 -*-

"""CID sequence module for working with CID sub object sequences (pipe groups, nodes, etc)."""
from ..names import SEQ_NAMES_DICT
from .cidseq import CidSeq, subclass_CidSeq
from .cidseqmaterials import SoilMaterialSeq, InterfMaterialSeq

PipeGroupSeq = subclass_CidSeq(SEQ_NAMES_DICT["pipe_groups"])
NodeSeq = subclass_CidSeq(SEQ_NAMES_DICT["nodes"])
ElementSeq = subclass_CidSeq(SEQ_NAMES_DICT["elements"])
BoundarySeq = subclass_CidSeq(SEQ_NAMES_DICT["boundaries"])
MaterialSeq = subclass_CidSeq(SEQ_NAMES_DICT["materials"])
FactorSeq = subclass_CidSeq(SEQ_NAMES_DICT["factors"])

__all__ = "PipeGroupSeq NodeSeq ElementSeq BoundarySeq SoilMaterials InterfMaterialSeq MaterialSeq FactorSeq".split()
