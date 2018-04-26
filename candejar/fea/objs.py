# -*- coding: utf-8 -*-

"""Module for working with typical FEA type objects."""

from dataclasses import dataclass
from typing import Optional, TypeVar, Generic

#  NOTE: PipeGroup objects can contain a wide variety of attributes; need to find a way to accommodate
@dataclass
class PipeGroup:
    type_: str = ""  # ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE

#  NOTE: Material objects can contain a wide variety of attributes; need to find a way to accommodate
@dataclass
class Material:
    model: int = 1  # 1: Isotropic, 2: Orthotropic, 3: Duncan/Selig, 4: Overburden,
                    # 5: Extended Hardin, 6: Interface, 7: Composite Link, 8: Mohr/Coulomb
    density: float = 0.0
    name: str = ""
    # layers: InitVar[Sequence[Layer]] = None <- will use for overburden soil implementation if ever needed

@dataclass
class Node:
    x: float = 0.0
    y: float = 0.0

NodeORNodeNum = TypeVar("NodeORNodeNum", int, Node)


@dataclass
class Element(Generic[NodeORNodeNum]):
    i: NodeORNodeNum
    j: NodeORNodeNum
    k: Optional[NodeORNodeNum] = None
    l: Optional[NodeORNodeNum] = None
    mat: int = 1
    step: int = 1
    interflink: int = 0
    death: int = 0


@dataclass
class Boundary:
    node: Node
    xcode: int = 0
    xvalue: float = 0.0
    ycode: int = 0
    yvalue: float = 0.0
    angle: float = 0.0
    pressure1: float = 0.0
    pressure2: float = 0.0


@dataclass
class Factor:
    start: int
    last: int
    factor: float = 1.0
    comment: str = ""
