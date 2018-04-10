# -*- coding: utf-8 -*-

"""Names relating the line types, fea types, CidSubObj subclasses, and the cid object group names together."""

from ...cid import A2, C3, C4, C5, D1, E1
from ... import fea

# below for auto generating the CidSubObj subclasses
SEQ_NAMES = ("pipe_groups", "nodes", "elements", "boundaries", "materials", "factors")
LINE_TYPES = (A2, C3, C4, C5, D1, E1)
SUB_OBJ_CLASS_NAMES = ("PipeGroup", "Node", "Element", "Boundary", "Material", "Factor")
SUB_OBJ_CLASS_DICT = dict(zip(LINE_TYPES, SUB_OBJ_CLASS_NAMES))
SEQ_NAME_DICT = dict(zip(SEQ_NAMES, LINE_TYPES))

TYPE_DICT = {A2: fea.PipeGroup, C3: fea.Node, C4: fea.Element, C5: fea.Boundary, D1: fea.Material, E1: fea.Factor}
