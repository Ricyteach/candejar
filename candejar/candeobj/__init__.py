# -*- coding: utf-8 -*-

"""Sub package for working with CANDE problems as a Python data model object."""

from .materials import PipeGroup, Node, Element, Boundary, Material, Factor
from ..cid import A2, C3, C4, C5, D1, E1

__all__ = "PipeGroup, Node, Element, Boundary, Material, Factor".split(", ")

FEA_TYPE_DICT = {A2: PipeGroup, C3: Node, C4: Element, C5: Boundary, D1: Material, E1: Factor}
