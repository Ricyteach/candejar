# -*- coding: utf-8 -*-

"""Names relating the cid line types to the CidSeq subclasses"""

from ...cid import SEQ_LINE_TYPES

# below for auto generating the CidSeq subclasses
# `soilmaterials` and `interfmaterials` handled seperately because classes not auto generated (they are sub pieces of `materials`)
SEQ_CLASS_NAMES = ("PipeGroupSeq", "NodeSeq", "ElementSeq", "BoundarieSeq", "MaterialSeq", "FactorSeq")
SEQ_CLASS_DICT = dict(zip(SEQ_LINE_TYPES, SEQ_CLASS_NAMES))

# NOTE: this is for completeness; the InterfMaterials and SoilMaterials classes are not auto generated
MAT_SEQ_CLASS_NAMES = ("SoilMaterialSeq", "InterfMaterialSeq")
ALL_SEQ_CLASS_NAMES = SEQ_CLASS_NAMES + MAT_SEQ_CLASS_NAMES
