# -*- coding: utf-8 -*-

"""Names relating the cid line types to the CidObj attributes"""

from ..cid import SEQ_LINE_TYPES, A2, C3, C4, C5, E1, D1
from .. import fea

# below for sequence attributes of CidObj instances
SEQ_NAMES = ("pipe_groups", "nodes", "elements", "boundaries", "materials", "factors")
SEQ_LINE_TYPE_NAME_DICT = dict(zip(SEQ_LINE_TYPES, SEQ_NAMES))

MAT_LINE_TYPES = (D1, D1)
MAT_SEQ_NAMES = ("soilmaterials", "interfmaterials")
ALL_SEQ_NAMES = SEQ_NAMES + MAT_SEQ_NAMES

SEQ_TYPES_DICT = dict(zip(SEQ_NAMES + MAT_SEQ_NAMES, SEQ_LINE_TYPES + MAT_LINE_TYPES))
FEA_TYPE_DICT = {A2: fea.PipeGroup, C3: fea.Node, C4: fea.Element,
                 C5: fea.Boundary, D1: fea.Material, E1: fea.Factor}
SEQ_NAMES_DICT = dict(zip(SEQ_LINE_TYPES, SEQ_NAMES))

# below for sequence total attributes of CidObj instances; using nmaterials
# (instead of nsoilmaterials and ninterface materials) because nmterials is
# used when iterating ALL lines types of D1 (for reading/writing only since
# .cid file treats them the same)
SEQ_LINE_TYPE_TOTALS = ("ngroups", "nnodes", "nelements",
                        "nboundaries", "nmaterials", "nsteps")
SEQ_LINE_TYPE_TOTAL_DICT = dict(zip(SEQ_LINE_TYPES, SEQ_LINE_TYPE_TOTALS))
