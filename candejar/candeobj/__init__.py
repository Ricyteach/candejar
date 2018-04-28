# -*- coding: utf-8 -*-

"""Sub package for working with CANDE problems as a Python data model object."""

from . import materials, pipe_groups, level3
from .materials import Material
from .pipe_groups import  PipeGroup
from .level3 import  Node, Element, Boundary, Factor
from ..cid import A2, C3, C4, C5, D1, E1

__all__ = "level3 pipe_groups materials".split()

FEA_TYPE_DICT = {A2: PipeGroup, C3: Node, C4: Element,
                 C5: Boundary, D1: Material, E1: Factor}
