# -*- coding: utf-8 -*-

"""Operations for working with geometries."""
from typing import NamedTuple, Tuple, Iterator, Optional, Dict, List, DefaultDict, Counter, Set, Union, TypeVar

import shapely.geometry as geo
import shapely.ops as ops
import shapely.affinity as affine

from utilities.sequence_tools import orient_seq
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
    Lside, Rside = get_LRsides(Aside, Bside, splitter)
    return SplitGeometry(*(side.intersection(geom) for side in (Lside, Rside)))


geoLine = TypeVar("geoLine", geo.LineString, geo.LinearRing)
String_or_Ring = Union[geo.LineString, geo.LinearRing]

def iter_oriented_line_pt_idx(to_orient: String_or_Ring, path: String_or_Ring,
                              buffer: Optional[float] = None) -> Iterator[int]:
    """Yields a subset of the point indexes of a line based upon the orientation of the path. Note: if no
    buffer is provided the line points must be on the path.

    Point indexes are iterated based upon the order in which they are captured by the path. A point index is
    captured and yielded if its associated point:

        1. Is within the buffer distance of the current path segment (default buffer is zero)
        2. Has not been captured by a previous segment (the first capturing path segment lays claim to each line point)
        3. If a segment captures multiple points: is the next closest point to the *first* path segment point

    If a line is ring-like the final ring point will be removed.
    """
    if buffer is None:
        buffer = 0
    else:
        buffer = float(buffer)
    coords_to_orient = to_orient.coords
    # note: even after the following block, a LineString could still be ring-like; more handling required way below
    if isinstance(to_orient,geo.LinearRing):
        coords_to_orient=coords_to_orient[:-1]
    points_to_orient = geo.MultiPoint(coords_to_orient)
    path_segments = geo.MultiLineString(list(iter_segments(path)))

    lpdx_to_sdx_dict: DefaultDict[int,Set[int]] = DefaultDict(set)
    lpdx_to_min_dist_dict: Dict[int,float] = dict()
    sdx_to_lpdx_dict: Dict[int, List[int]] = DefaultDict(list)
    lpdx: int
    lp: geo.Point
    for (lpdx,lp) in enumerate(points_to_orient):
        seg: geo.LineString
        # match line point indexes with path segment indexes
        for sdx, seg in enumerate(path_segments):
            d: float = lp.distance(seg)
            # associate each line point index with path segment indexes within the buffer
            if d<=lpdx_to_min_dist_dict.get(lpdx,buffer):
                if d<lpdx_to_min_dist_dict.get(lpdx, buffer):
                    # keep only the closest path segment
                    lpdx_to_sdx_dict[lpdx].clear()
                lpdx_to_min_dist_dict[lpdx]=d
                lpdx_to_sdx_dict[lpdx].add(sdx)
        # point may fall on multiple segments
        try:
            # the Jacqueline Rule: the first segment in the series captures the point
            closest_sdx = min(lpdx_to_sdx_dict[lpdx])
        except ValueError:
            # un-captured lp (lp not within buffer for any segments)
            pass
        else:
            # captured lp
            sdx_to_lpdx_dict[closest_sdx].append(lpdx)
    del lpdx,lp
    sdx_to_lpdx_sorted = dict(sorted(sdx_to_lpdx_dict.items()))
    # now have a 1 to 1 relationship for segments and points (but may be multiple points per segment)
    lpdx_bag: List[int]
    if all(len(lpdx_bag)==1 for lpdx_bag in sdx_to_lpdx_sorted.values()):
        # ALL 1 to 1
        yield from (lpdx for (lpdx,) in sdx_to_lpdx_sorted.values())
    else:
        # some not 1 to 1
        sdx: int
        for sdx, lpdx_bag in sdx_to_lpdx_sorted.items():
            if len(lpdx_bag)==1:
                # 1 to 1
                yield lpdx_bag[0]
            else:
                # not 1 to 1; iterate based on distance to first segment point
                dist_lpdx_sub_list: List[Tuple[float,int]] = []
                seg_point = geo.Point(path_segments[sdx].coords[0])
                lpdx: int
                for lpdx in lpdx_bag:
                    d = seg_point.distance(points_to_orient[lpdx])
                    dist_lpdx_sub_list.append((d,lpdx))
                dist_lpdx_sub_list_sorted = sorted(dist_lpdx_sub_list)
                yield from (lpdx for _,lpdx in dist_lpdx_sub_list_sorted)


def iter_segments(line: geoLine) -> Iterator[geo.LineString]:
    """Yield the line segments that make up some geometric line or ring."""
    if isinstance(line,geo.LinearRing):
        line=geo.LineString(line.coords[:-1])
    yield from (geo.LineString(line.coords[x:x + 2]) for x in range(len(line.coords) - 1))


def get_LRsides(Aside: geo.base.BaseGeometry,
                Bside: geo.base.BaseGeometry,
                splitter: geo.base.BaseGeometry) -> Tuple[geo.base.BaseGeometry, geo.base.BaseGeometry]:
    """Determine the 'left' and 'right' sides of an already split geometry"""
    Alist = list(Aside) if hasattr(Aside, "__iter__") else [Aside]
    Blist = list(Bside) if hasattr(Bside, "__iter__") else [Bside]
    result_dict = dict(A = dict(right=(Bside, Aside), left=(Aside, Bside)),
                       B = dict(right=(Aside, Bside), left=(Bside, Aside)))
    for sidelist, side_name in zip((Alist,Blist),("A","B")):
        for p in sidelist:
            # step 1: get the line strings that make up the common edges of the sides and the splitter
            common_edges = p.boundary.intersection(splitter)
            common_edges = list(common_edges) if hasattr(common_edges, "__iter__") else [common_edges]
            # step 2: iterate over the common_edges
            for common_edge in common_edges:
                # step 3: orient line_string so that it goes in same order of the splitter orientation
                i_points_idxs = iter_oriented_line_pt_idx(common_edge, splitter)
                common_edge = geo.LineString(orient_seq(list(common_edge.coords), i_points_idxs))
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


def splitLR_(geom: geo.base.BaseGeometry, splitter: geo.base.BaseGeometry):
    left,right = [],[]
    split_geom = ops.split(geom, splitter)
    if len(split_geom)==1:
        raise GeometryError("splitter did not split the geometry")
    pdx: int
    p: geo.Polygon
    for pdx,p in enumerate(split_geom):
        if not isinstance(p,geo.Polygon):
            raise GeometryError("split operation resulted in a non-polygon (not supported)")
        common_edges = p.boundary.intersection(splitter)
        common_edges = list(common_edges) if hasattr(common_edges, "__iter__") else [common_edges]
        ceidx: int
        common_edge: geo.LineString
        ccw_orientations: Dict[int,bool] = dict()
        for ceidx, common_edge in enumerate(common_edges):
            i_points_idxs = iter_oriented_line_pt_idx(common_edge, splitter)
            common_edge_oriented = geo.LineString(orient_seq(list(common_edge.coords), i_points_idxs))
            p_points_idxs = iter_oriented_line_pt_idx(p.boundary, common_edge_oriented)
            p_oriented = geo.Polygon(orient_seq(list(p.boundary.coords), p_points_idxs))
            p_boundary: geo.LinearRing = p_oriented.boundary
            ccw_orientations[ceidx]=p_boundary.is_ccw
        if all(ccw_orientations.values()):
            left.append(p)
        elif all(not ccw for ccw in ccw_orientations.values()):
            right.append(p)
        else:
            lookup_text = {True:"CCW", False:"CW"}
            ambiguity_explanation = ", ".join(f"{ceidx}: {lookup_text[is_ccw]}" for ceidx,is_ccw in ccw_orientations.items())
            raise GeometryError(f"split polygon index {pdx:d} has ambiguous orientation\n\tcommon edge index {ambiguity_explanation}")
    if len(left)==1:
        left = left[0]
    else:
        left = geo.MultiPolygon(left)
    if len(right)==1:
        right = right[0]
    else:
        right = geo.MultiPolygon(right)
    return SplitGeometry(left, right)
