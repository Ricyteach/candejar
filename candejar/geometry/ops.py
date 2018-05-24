# -*- coding: utf-8 -*-

"""Operations for working with geometries."""

from typing import NamedTuple, Tuple, Iterator, Optional

import shapely.geometry as geo
import shapely.ops as ops
import shapely.affinity as affine

from ..utilities.sequence_tools import iter_nn
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


def _orient_line_string(line_string: geo.LineString, path_string: geo.LineString,
                        buffer: Optional[float]=None) -> geo.LineString:
    if buffer is None:
        buffer = 0
    else:
        buffer = float(buffer)
    line_string_points = geo.MultiPoint(line_string.coords)
    path_string_segments = geo.MultiLineString(iter_segments(path_string))
    segments_distances = {}
    for point_idx,line_string_point in enumerate(line_string_points):
        point_dict = {}
        for s_idx,(s,d) in enumerate(iter_nn(line_string_point, path_string_segments, lambda p,l: p.distance(l))):
            if d<=buffer:
                point_dict[s_idx] = d
        try:
            closest_distance = min(point_dict.values())
        except ValueError as e:
            continue
        closest_segments = [(s_idx,d) for s_idx,d in point_dict.items() if d==closest_distance]
        segments_distances[point_idx] = closest_segments
    if len(segments_distances) < 2:
        raise GeometryError(f"The line_string must have at minimum two nodes that are within the buffer "
                            f"({buffer:.4f}) of the path_string")
    if all(len(closest_segments)==1 for closest_segments in segments_distances.values()):
        # 1 to 1 relationship for points and segments
        segment_indexes = [s_idx for p_idx,((s_idx,d),) in segments_distances.items()]
    else:
        # points fall on multiple segments
        segment_indexes = []
        for p_idx,closest_segments in segments_distances.items():
            if len(closest_segments) == 1:
                segment_indexes.append(closest_segments[0][0])
            else:
                # handle point falling on multiple segments
                raise NotImplementedError()
    current_order = [point_idx for point_idx in range(len(line_string_points)) if point_idx in segments_distances]
    correct_order = []
    for s_idx in segment_indexes:



def iter_segments(line_string: geo.LineString) -> Iterator[geo.LineString]:
    yield from (geo.LineString(line_string.coords[x:x+2]) for x in range(len(line_string.coords)-1))


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
