# -*- coding: utf-8 -*-

"""CID sequence module for working with CID sub object sequences (pipe groups, nodes, etc)."""
from .names import SEQ_NAMES
from .cidseq import CidSeq, subclass_CidSeq
from .cidseqmaterials import SoilMaterials, InterfMaterials

PipeGroups = subclass_CidSeq(SEQ_NAMES["pipe_groups"])
Nodes = subclass_CidSeq(SEQ_NAMES["nodes"])
Elements = subclass_CidSeq(SEQ_NAMES["elements"])
Boundaries = subclass_CidSeq(SEQ_NAMES["boundaries"])
Factors = subclass_CidSeq(SEQ_NAMES["factors"])

__all__ = "PipeGroups Nodes Elements Boundaries SoilMaterials InterfMaterials Factors".split()
