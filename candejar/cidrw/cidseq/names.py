# -*- coding: utf-8 -*-

"""Names relating the line types, fea types, CidSeq subclasses, and the cid object group names together."""

from ...cid import A2, C3, C4, C5, D1, E1
from ... import fea

# below for auto generating the CidSeq subclasses
# none for `soilmaterials` and `interfmaterials` because classes not auto generated (they are sub pieces of `materials`)
SEQ_NAMES = {"pipe_groups": A2, "nodes": C3, "elements": C4, "boundaries": C5, "soilmaterials": None, "interfmaterials": None, "materials": D1, "factors": E1}
SEQ_CLASS_NAMES = ("PipeGroups", "Nodes", "Elements", "Boundaries", "SoilMaterials", "InterfMaterials", "Materials", "Factors")
SEQ_CLASS_DICT = dict(zip(SEQ_NAMES.values(), SEQ_CLASS_NAMES))
SEQ_CLASS_DICT.pop(None)

TYPE_DICT = {A2: fea.PipeGroup, C3: fea.Node, C4: fea.Element, C5: fea.Boundary, D1: fea.Material, E1: fea.Factor}
