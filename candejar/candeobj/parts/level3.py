# -*- coding: utf-8 -*-

"""Module for working with cande level 3 type objects."""

from __future__ import annotations
import enum
from dataclasses import dataclass
from typing import ClassVar, Iterable

from .. import exc
from ...utilities.decorators import init_kwargs
from ...utilities.mixins import GeoMixin, WithKwargsMixin


@init_kwargs
@dataclass(init=False)
class Node(WithKwargsMixin, GeoMixin, geo_type="Point"):
    num: int
    x: float
    y: float
    master: Node = None
    geo_type: ClassVar[str] = "Point"

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


@init_kwargs
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


@init_kwargs
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
