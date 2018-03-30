# -*- coding: utf-8 -*-

"""Sub package for reading/writing (parsing/formatting) .cid files as a single object."""

from ..cid import A2, C3, C4, C5, D1, E1
from .. import fea

SEQ_NAME_DICT = {"pipe_groups": A2, "nodes": C3, "elements": C4, "boundaries": C5, "soilmaterials": D1, "interfmaterials": D1, "factors": E1}
SEQ_CLASS_TUP = ("PipeGroups", "Nodes", "Elements", "Boundaries", "SoilMaterials", "InterfMaterials", "Factors")
SEQ_CLASS_DICT = dict(zip(SEQ_NAME_DICT, SEQ_CLASS_TUP))
TYPE_DICT = {A2: fea.PipeGroup, C3: fea.Node, C4: fea.Element, C5: fea.Boundary, D1: fea.Material, E1: fea.Factor}
