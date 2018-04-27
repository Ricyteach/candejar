# -*- coding: utf-8 -*-

"""Module for working with cande level 3 type objects."""

from dataclasses import dataclass
from typing import TypeVar, Generic, Optional


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
class Boundary(Generic[NodeORNodeNum]):
    node: NodeORNodeNum
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

