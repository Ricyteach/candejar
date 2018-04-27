# -*- coding: utf-8 -*-

"""Names relating the cid line types to the CidSubObj subclasses"""

# below for auto generating the CidSubObj subclasses
from ...cid import SEQ_LINE_TYPES, \
    D2Isotropic, D2Duncan, D3Duncan, D4Duncan, D2Interface, D2MohrCoulomb,\
    B1Alum, B2AlumA, B2AlumDWSD, B2AlumDLRFD, B3AlumADLRFD, \
    B1Basic, B2Basic, \
    B1Steel, B2SteelA, B2SteelDWSD, B2SteelDLRFD, B2bSteel, B2cSteel, B2dSteel, B3SteelADLRFD, \
    B1Plastic, B2Plastic, B3PlasticAGeneral, B3PlasticASmooth, B3PlasticAProfile, B3bPlasticAProfile, B3PlasticDWSD, B3PlasticDLRFD, B4Plastic, \
    B1Concrete, B2Concrete, B3Concrete, B4ConcreteCase1_2, B4ConcreteCase3, B4bConcreteCase3, B4ConcreteCase4, B4ConcreteCase5, B5Concrete

SUB_OBJ_CLASS_NAMES = ("PipeGroup", "Node", "Element", "Boundary", "Material", "Factor")
SUB_OBJ_CLASS_DICT = dict(zip(SEQ_LINE_TYPES, SUB_OBJ_CLASS_NAMES))

PIPE_GROUP_TYPE_NAMES = "ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE".split(", ")
PIPE_GROUP_CLASS_NAMES = tuple(s.capitalize() for s in PIPE_GROUP_TYPE_NAMES)
PIPE_GROUP_CLASS_DICT = dict(zip(PIPE_GROUP_TYPE_NAMES, PIPE_GROUP_CLASS_NAMES))

# only including materials interesting in using
# TODO: add other materials later
MATERIAL_CLASS_DICT = {1: "Isotropic", 3: "DuncanSelig", 6: "Interface", 8: "MohrCoulomb"}
MATERIAL_DELEGATES_DICT = {1: (D2Isotropic,), 3: (D2Duncan, D3Duncan, D4Duncan,), 6: (D2Interface,), 8: (D2MohrCoulomb,)}
