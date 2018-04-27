# -*- coding: utf-8 -*-

"""Names relating the cid line types to the CidSubObj subclasses"""

# below for auto generating the CidSubObj subclasses
from ...cid import SEQ_LINE_TYPES

SUB_OBJ_CLASS_NAMES = ("PipeGroup", "Node", "Element", "Boundary", "Material", "Factor")
SUB_OBJ_CLASS_DICT = dict(zip(SEQ_LINE_TYPES, SUB_OBJ_CLASS_NAMES))

PIPE_GROUP_TYPE_NAMES = "ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE".split(", ")
PIPE_GROUP_CLASS_NAMES = tuple(s.capitalize() for s in PIPE_GROUP_TYPE_NAMES)
PIPE_GROUP_CLASS_DICT = dict(zip(PIPE_GROUP_TYPE_NAMES, PIPE_GROUP_CLASS_NAMES))

# only including materials interesting in using
# TODO: add other materials later
SOIL_MATERIAL_DICT = {1: "Isotropic", 3: "DuncanSelig", 6: "Interface", 8: "MohrCoulomb"}
