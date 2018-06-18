# -*- coding: utf-8 -*-

"""Module for working with cande level 3 type objects."""

from dataclasses import dataclass
from typing import ClassVar


class WithKwargsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        for k, v in kwargs.items():
            setattr(self, k, v)


@dataclass(init=False)
class Node(WithKwargsMixin):
    num: int
    x: float
    y: float
    geo_type: ClassVar[str] = "Point"

    def __init__(self, num: int, x: float, y: float, **kwargs) -> None:
        self.num, self.x, self.y = num, x, y
        super().__init__(**kwargs)

    @property
    def __geo_interface__(self):
        return dict(type=self.geo_type, coordinates=(self.x, self.y))


@dataclass(init=False)
class Element(WithKwargsMixin):
    num: int
    i: int
    j: int
    k: int = 0
    l: int = 0
    mat: int = 0
    step: int = 0
    interflink: int = 0
    death: int = 0

    def __init__(self, num: int, i: int, j: int, k: int = 0, l: int = 0, *, mat: int = 0, step: int = 0,
                 interflink: int = 0, death: int = 0, **kwargs) -> None:
        self.num, self.i, self.j, self.k, self.l, self.mat, self.step, self.interflink, self.death = num, i, j, k, l, mat, step, interflink, death
        super().__init__(**kwargs)


@dataclass(init=False)
class Boundary(WithKwargsMixin):
    node: int
    xcode: int = 0
    xvalue: float = 0.0
    ycode: int = 0
    yvalue: float = 0.0
    angle: float = 0.0
    pressure1: float = 0.0
    pressure2: float = 0.0

    def __init__(self, node: int, xcode: int = 0, xvalue: float = 0.0, ycode: int = 0, yvalue: float = 0.0, *,
                 angle: float = 0.0, pressure1: float = 0.0, pressure2: float = 0.0, **kwargs) -> None:
        self.node, self.xcode, self.xvalue, self.ycode, self.yvalue, self.angle, self.pressure1, self.pressure2 = node, xcode, xvalue, ycode, yvalue, angle, pressure1, pressure2
        super().__init__(**kwargs)
