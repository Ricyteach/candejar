# -*- coding: utf-8 -*-

"""Module for working with cande level 3 type objects."""

import enum
from dataclasses import dataclass
from typing import ClassVar

from .. import exc
from ...utilities.mixins import GeoMixin, WithKwargsMixin


@dataclass(init=False)
class Node(WithKwargsMixin, GeoMixin, geo_type="Point"):
    num: int
    x: float
    y: float
    geo_type: ClassVar[str] = "Point"

    def __init__(self, num: int, x: float, y: float, **kwargs) -> None:
        self.num = num
        self.x = x
        self.y = y
        super().__init__(**kwargs)

    @property
    def __geo_interface__(self):
        return dict(type=self.geo_type, coordinates=(self.x, self.y))


class ElementCategory(enum.Enum):
    PIPE = -1
    SOIL = 0
    INTERFACE = 1
    FIXED = 8
    PINNED = 9
    TRANSVERSE = 10
    LONGITUDINAL = 11


@dataclass(init=False)
class Element(WithKwargsMixin, GeoMixin, geo_type="Polygon"):
    num: int
    i: int
    j: int
    k: int = 0
    l: int = 0
    mat: int = 0
    step: int = 0
    connection: int = 0
    death: int = 0

    def __init__(self, num: int, i: int, j: int, k: int = 0, l: int = 0, *,
                 mat: int = 0, step: int = 0, connection: int = 0,
                 death: int = 0, **kwargs) -> None:
        self.num = num
        self.i = i
        self.j = j
        self.k = k
        self.l = l
        self.mat = mat
        self.step = step
        self.connection = connection
        self.death = death
        super().__init__(**kwargs)

    def remove_repeats(self):
        """Change repeated node numbers to zero."""
        i, j = (getattr(self, attr) for attr in "ij")
        for a, b in zip((i, i, j, j), "klkl"):
            if a == getattr(self, b):
                setattr(self, b, 0)

    @property
    def category(self) -> ElementCategory:
        connection_value = self.connection
        if not connection_value:
            # regular geometric element
            if not self.k and not self.l:
                return ElementCategory["PIPE"]
            else:
                return ElementCategory["SOIL"]
        else:
            # interface or link element
            try:
                return ElementCategory(connection_value)
            except ValueError as e:
                raise exc.CandeValueError(f"Invalid field value for Connection: "
                                          f"{connection_value}") from e


@dataclass(init=False)
class Boundary(WithKwargsMixin, GeoMixin, geo_type="Node"):
    node: int
    xcode: int = 0
    xvalue: float = 0.0
    ycode: int = 0
    yvalue: float = 0.0
    angle: float = 0.0
    step: int = 0
    pressure1: float = 0.0
    pressure2: float = 0.0

    def __init__(self, node: int, xcode: int = 0, xvalue: float = 0.0,
                 ycode: int = 0, yvalue: float = 0.0, *, angle: float = 0.0,
                 step: int = 0, pressure1: float = 0.0, pressure2: float = 0.0,
                 **kwargs) -> None:
        self.node = node
        self.xcode = xcode
        self.xvalue = xvalue
        self.ycode = ycode
        self.yvalue = yvalue
        self.angle = angle
        self.step = step
        self.pressure1 = pressure1
        self.pressure2 = pressure2
        super().__init__(**kwargs)
