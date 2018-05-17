# -*- coding: utf-8 -*-

"""Operations for working with geometries."""

from typing import NamedTuple, Tuple

import shapely.geometry as geo
import shapely.ops as ops

from .exc import GeometryError

class SplitGeometry(NamedTuple):
    left: geo.base.BaseGeometry
    right: geo.base.BaseGeometry

def splitLR(geom: geo.base.BaseGeometry,
            splitter: geo.base.BaseGeometry) -> SplitGeometry:
    """Split a geometry into a 'left' and 'right' side using the shapely API"""
    if not isinstance(splitter, geo.LineString):
        raise GeometryError("The splitter must be a LineString")
    if not splitter.is_simple:
        raise GeometryError("Only simple splitter objects allowed")
    if hasattr(geom, "__iter__"):
        raise GeometryError("Geometry collections not allowed")
    geom = geo.GeometryCollection([geom])
    geom_extents = geo.GeometryCollection([*geom, splitter]).minimum_rotated_rectangle
    sides = ops.split(geom_extents, splitter)
    try:
        Aside, Bside = sides
    except TypeError:
        # only 1 result - rotated rectangle wasn't split
        if len(ops.split(geom, splitter)) == 1:
            # geom isn't split by splitter
            raise GeometryError("the splitter does not appear to split the geometry")
        else:
            # splitter too small for algorithm
            raise GeometryError("the splitter must extend beyond minimum_rotated_rectangle of the combined geometry")
    # determine Lside and Rside here
    Lside, Rside = _get_LRsides(Aside, Bside, splitter)
    return SplitGeometry(*(side.intersection(geom) for side in (Lside, Rside)))

def _get_LRsides(Aside: geo.base.BaseGeometry,
                 Bside: geo.base.BaseGeometry,
                 splitter: geo.base.BaseGeometry) -> Tuple(geo.base.BaseGeometry,
                                                           geo.base.BaseGeometry):
    """Determine the 'left' and 'right' sides of an already split geometry"""
    return Aside,Bside
