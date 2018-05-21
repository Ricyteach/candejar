# -*- coding: utf-8 -*-

"""Operations for working with geometries."""

from typing import NamedTuple, Tuple, Iterator

import shapely.geometry as geo
import shapely.ops as ops
import shapely.affinity as affine

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

def _orient_line_string(line_string: geo.LineString, path_string: geo.LineString) -> geo.LineString:
    # get rid of any duplicate path coordinates
    seen = set()
    seenadd = seen.add  # optimization
    path_string_coords = [pair for pair in path_string.coords if not (pair in seen or seenadd(pair))]
    path_string_points = geo.MultiPoint(path_string_coords)
    # check that at least 2 line_string nodes are on the path_string
    line_string_coords = tuple(line_string.coords)
    line_string_points = geo.MultiPoint(line_string.coords)
    common_coords = [pair for pair in path_string_coords if pair in line_string_coords]
    if len(common_coords)<2:
        raise GeometryError("The path_string must have at minimum two nodes that appear in the line_string")
    for line_coord,line_coord_idx in enumerate(line_string_coords):
        if line_coord == common_coords[0]:
            first_idx = line_coord_idx
            break
    for line_coord,line_coord_idx in enumerate(line_string_coords):
        if line_coord == common_coords[1]:
            second_idx = line_coord_idx
            break
    if first_idx<second_idx:
        return line_string
    else:
        return geo.LineString(reversed(line_string_coords))


def iter_segments(line_string: geo.LineString) -> Iterator[geo.LineString]:
    yield from (geo.LineString(line_string.coords[x:x+2]) for x in range(len(line_string.coords)))

def _get_LRsides(Aside: geo.base.BaseGeometry,
                 Bside: geo.base.BaseGeometry,
                 splitter: geo.base.BaseGeometry) -> Tuple[geo.base.BaseGeometry, geo.base.BaseGeometry]:
    """Determine the 'left' and 'right' sides of an already split geometry"""
    Alist = list(Aside) if hasattr(Aside, "__iter__") else [Aside]
    Blist = list(Bside) if hasattr(Bside, "__iter__") else [Bside]
    result_dict = dict(A = dict(right=(Bside, Aside), left=(Aside, Bside)),
                       B = dict(right=(Aside, Bside), left=(Bside, Aside)))
    for sidelist, side_name in zip((Alist,Blist),("A","B")):
        for x in sidelist:
            # step 1: get the line strings that make up the comment edges of the sides and the splitter
            common_edges = x.boundary.intersection(splitter)
            common_edges = list(common_edges) if hasattr(common_edges, "__iter__") else [common_edges]
            # step 2: iterate over the common_edges
            for common_edge in common_edges:
                # step 3: orient line_string so that it goes in same order of the splitter orientation
                common_edge = _orient_line_string(common_edge, splitter)
                # step 4: iterate over the line segments making up each common_edge
                for segment in iter_segments(common_edge):
                    # step 4a: get the segment midpoint
                    midpoint = segment.interpolate(0.5, normalized=True)
                    # step 4b: get the `x` exterior edge
                    a_edge = x.boundary.difference(common_edge)
                    # step 4c: make perpendicular segment at midpoint, increase by 1000x length each time until
                    # extends beyond the `x` bounding box; 90 deg rotation means
                    perp_segment = affine.rotate(segment, 90, midpoint)
                    factor = 1000
                    while True:
                        scaled_perp_segment: geo.LineString = affine.scale(perp_segment,factor,factor,factor,midpoint)
                        if scaled_perp_segment.within(x.minimum_rotated_rectangle):
                            factor *= 1000
                            continue
                        break
                    # step 4d: get left and right midpoint perpendiculars
                    l_perpendicular = geo.LineString((midpoint, scaled_perp_segment.interpolate(1.0, normalized=True)))
                    r_perpendicular = geo.LineString((midpoint, scaled_perp_segment.interpolate(0.0, normalized=True)))
                    # step 4e: find the intersections from midpoint to the `x` exterior on left/right side
                    l_intersections = l_perpendicular.intersection(a_edge)
                    r_intersections = r_perpendicular.intersection(a_edge)
                    # step 4f: check to see if both sides had no intersections? can this happen...?
                    if all(i.is_empty for i in (l_intersections,r_intersections)):
                        # give up; try the next segment
                        continue
                    # step 4g: the side with intersections tells us which side `x` is on
                    if l_intersections.is_empty:
                        # the side is in on the right
                        return result_dict[side_name]["right"]
                    elif r_intersections.is_empty:
                        # the side is in on the left
                        return result_dict[side_name]["left"]
                    else:
                        # could try to figure it out when intersections occur on both sides but let's just move on
                        continue
    else:
        raise GeometryError("Failed to figure out which side is which (left and right)")
