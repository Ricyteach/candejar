# -*- coding: utf-8 -*-

"""Module for working with cande level 3 type objects."""

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

from .bases import NodeNum, MatNum, StepNum, CodeNum, CandeFloat, CandeStr

@dataclass
class Node:
    x: CandeFloat = 0.0
    y: CandeFloat = 0.0

NodeORNodeNum = TypeVar("NodeORNodeNum", NodeNum, Node)

@dataclass
class Element(Generic[NodeORNodeNum]):
    i: NodeORNodeNum
    j: NodeORNodeNum
    k: Optional[NodeORNodeNum] = None
    l: Optional[NodeORNodeNum] = None
    mat: MatNum = 1
    step: StepNum = 1
    interflink: int = 0
    death: StepNum = 0


@dataclass
class Boundary(Generic[NodeORNodeNum]):
    node: NodeORNodeNum
    xcode: CodeNum = 0
    xvalue: CandeFloat = 0.0
    ycode: CodeNum = 0
    yvalue: CandeFloat = 0.0
    angle: CandeFloat = 0.0
    pressure1: CandeFloat = 0.0
    pressure2: CandeFloat = 0.0


@dataclass
class Factor:
    start: StepNum
    last: StepNum
    factor: CandeFloat = 1.0
    comment: CandeStr = ""
