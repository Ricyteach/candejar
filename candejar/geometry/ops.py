# -*- coding: utf-8 -*-

"""Operations for working with geometries."""

from typing import NamedTuple

import shapely.geometry as geo
import shapely.ops as ops

from .exc import GeometryError

class SplitGeometry(NamedTuple):
    left: geo.base.BaseGeometry
    right: geo.base.BaseGeometry

def splitLR(geom: geo.base.BaseGeometry,
            splitter: geo.base.BaseGeometry) -> SplitGeometry:
    """Split a geometry into a 'left' and 'right' side using the shapely API"""
    if not splitter.is_simple:
        raise GeometryError("Only simple splitter objects allowed")
    geom = geo.GeometryCollection([geom])
    geom_extents = geo.GeometryCollection([*geom, splitter]).minimum_rotated_rectangle
    sides = ops.split(geom_extents, splitter)
    try:
        Aside, Bside = sides
    except TypeError:
        raise GeometryError("the splitter must extend beyond "
                            "minimum_rotated_rectangle of geom")
    return SplitGeometry(side.intersection(geom) for side in (Lside, Rside))
