# -*- coding: utf-8 -*-

"""Sub package for handling .cid file line sequence processing.

Pipe Line Processing Key
========================

A:      cid.mode == 'ANALYS' only
D:      cid.mode == 'DESIGN' only
AD:     cid.mode == 'ANALYS' or 'DESIGN'
WSD:    cid.method == 0 only
LRFD:   cid.method == 1 only
"""

from . import alum
from . import basic
# from . import concrete
from . import plastic
from . import steel


pipelookup = dict(
            ALUMINUM=alum.B1Alum,
            BASIC=basic.B1Basic,
            CONCRETE=NotImplemented,
            PLASTIC=plastic.B1Plastic,
            STEEL=steel.B1Steel,
            CONRIB=NotImplemented,
            CONTUBE=NotImplemented
            )
