# -*- coding: utf-8 -*-

"""Names relating the cid line types to the CidSubObj subclasses"""

# below for auto generating the CidSubObj subclasses
from ...cid import SEQ_LINE_TYPES

SUB_OBJ_CLASS_NAMES = ("PipeGroup", "Node", "Element", "Boundary", "Material", "Factor")
SUB_OBJ_CLASS_DICT = dict(zip(SEQ_LINE_TYPES, SUB_OBJ_CLASS_NAMES))
