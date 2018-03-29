# -*- coding: utf-8 -*-

"""Sub package for generic FEA object usage."""

from typing import TypeVar
from .objs import PipeGroup, Node, Element, Boundary, Material, Factor

__all__ = "PipeGroup, Node, Element, Boundary, Material, Factor".split(", ")

FEAObj = TypeVar("FEAObj", PipeGroup, Node, Element, Boundary, Material, Factor)
