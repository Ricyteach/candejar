# -*- coding: utf-8 -*-

"""Sub package for reading/writing (parsing/formatting) lines of .cid files."""
from typing import TypeVar

from .cidlineclasses import A1, A2, C1, C2, C3, C4, C5, E1, Stop, D1, D2Isotropic, D2Orthotropic, D2Duncan, D3Duncan, D4Duncan, D2Over, D2Hardin, D2HardinTRIA, D2Interface, D2Composite, D2MohrCoulomb, B1Alum, B2AlumA, B2AlumDWSD, B2AlumDLRFD, B3AlumADLRFD, B1Steel, B2SteelA, B2SteelDWSD, B2SteelDLRFD, B2bSteel, B2cSteel, B2dSteel, B3SteelADLRFD, B1Plastic, B2Plastic, B3PlasticAGeneral, B3PlasticASmooth, B3PlasticAProfile, B3bPlasticAProfile, B3PlasticDWSD, B3PlasticDLRFD, B4Plastic, B1Concrete, B2Concrete, B3Concrete, B4ConcreteCase1_2, B4ConcreteCase3, B4bConcreteCase3, B4ConcreteCase4, B4ConcreteCase5, B5Concrete, B1Basic, B2Basic
from .cidline import CidLine

CidSubLine = TypeVar("CidSubLine", A2, C3, C4, C5, D1, E1)

# below definitions for read/write of cid objects
SEQ_LINE_TYPES = (A2, C3, C4, C5, D1, E1)  # note: needs to be ordered
TOP_LEVEL_TYPES = set(SEQ_LINE_TYPES) | {A1, C1, C2, Stop}  # marks end of B1 etc. or D2 etc. sub lines
CIDL_FORMAT_TYPES = set(SEQ_LINE_TYPES) - {A2}  # lines types that can use cidL format
