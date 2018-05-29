# -*- coding: utf-8 -*-

"""Operations for working with geometries."""
from typing import NamedTuple, Tuple, Iterator, Optional, Dict, List, DefaultDict, Counter, Set, Union, TypeVar

import shapely.geometry as geo
import shapely.ops as ops
import shapely.affinity as affine

from ..utilities.sequence_tools import orient_seq
from .exc import GeometryError


class SplitGeometry(NamedTuple):
    left: geo.base.BaseGeometry
    right: geo.base.BaseGeometry

geoLine = TypeVar("geoLine", geo.LineString, geo.LinearRing)
String_or_Ring = Union[geo.LineString, geo.LinearRing]

def splitLR(geom: geo.base.BaseGeometry, splitter: String_or_Ring) -> SplitGeometry:
    """Split a geometry into a 'left' and 'right' side using the shapely API"""
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
            i_points_idxs = list(iter_oriented_line_pt_idx(common_edge, splitter))
            common_edge_oriented = geo.LineString(orient_seq(list(common_edge.coords), i_points_idxs))
            p_points_idxs = list(iter_oriented_line_pt_idx(p.boundary, common_edge_oriented))
            p_oriented = geo.Polygon(orient_seq(list(p.boundary.coords), p_points_idxs))
            p_boundary: geo.LinearRing = p_oriented.exterior
            ccw_orientations[ceidx]=p_boundary.is_ccw
        if all(ccw_orientations.values()):
            left.append(p)
        elif all(not ccw for ccw in ccw_orientations.values()):
            right.append(p)
        else:
            lookup_text = {True:"CCW", False:"CW"}
            ambiguity_explanation = ", ".join(f"{ceidx}: {lookup_text[is_ccw]}" for ceidx,is_ccw in ccw_orientations.items())
            raise GeometryError(f"split polygon index {pdx:d} has ambiguous orientation\n\tcommon edge index {ambiguity_explanation}")
    left = geo.MultiPolygon(left)
    right = geo.MultiPolygon(right)
    return SplitGeometry(left, right)


def iter_oriented_line_pt_idx(to_orient: String_or_Ring, path: String_or_Ring,
                              buffer: Optional[float] = None) -> Iterator[int]:
    """Yields a subset of the point indexes of a line based upon the orientation of the path. Note: if no
    buffer is provided the line points must be on the path.

    Point indexes are iterated based upon the order in which they are captured by the path. A point index is
    captured and yielded if its associated point:

        1. Is within the buffer distance of the current path segment (default buffer is zero)
        2. Has not been captured by a previous segment (the first capturing path segment lays claim to each line point)
        3. If a segment captures multiple points: is the next closest point to the *first* path segment point

    In the case of a ring-like line, if the repeated ring end point is captured then at least one of the immediate
    neighboring points must also be captured (error otherwise).

    Note that if a line orientation turns out to be ambiguous- e.g. the case where a path captures only index 0 and
    index 2 of a 4-point line- the line orientation is assumed to be the originally supplied orientation.
    """
    if buffer is None:
        buffer = 0
    else:
        buffer = float(buffer)
    if isinstance(to_orient, (geo.LineString, geo.LinearRing)):
        if not to_orient.is_simple:
            raise GeometryError("simple linear objects are required for orientation")
    else:
        raise GeometryError("a line like geometry object is required")

    # the path will decide the resulting line index order
    coords_to_orient = list(to_orient.coords)
    points_to_orient = geo.MultiPoint(coords_to_orient)
    path_segments = geo.MultiLineString(list(iter_segments(path)))
    if len(path_segments)==0:
        raise GeometryError("failed to break path into segments")

    # sorting dictionaries
    lpdx_to_sdx_dict: DefaultDict[int,Set[int]] = DefaultDict(set)
    lpdx_to_min_dist_dict: Dict[int,float] = dict()
    sdx_to_lpdx_dict: Dict[int, List[int]] = DefaultDict(list)

    if to_orient.is_closed:
        # handle ring-like line
        repeated_point = points_to_orient[0]
        # get the capturing segment
        min_distance_to_repeated_point = min(repeated_point.distance(seg) for seg in path_segments)
        # if the repeated ring end point is NOT captured, ignore; otherwise this needs handling
        if min_distance_to_repeated_point<=buffer:
            # repeated point is captured - needs handling
            p_second, p_second_to_last = points_to_orient[1], points_to_orient[-2]
            # get min distances for second and second-to-last points (are separate points since the line is simple)
            d_second = min(p_second.distance(seg) for seg in path_segments)
            d_second_to_last = min(p_second_to_last.distance(seg) for seg in path_segments)
            # at least one of the two neighboring points to the repeated ring end point must be captured
            captured_dict = {1: d_second<=buffer, -2: d_second_to_last<=buffer}
            if True in captured_dict.values():
                if captured_dict[1] and captured_dict[-2]:
                    # both neighbors captured; discard both ring end points (they aren't needed)
                    points_to_orient = geo.MultiPoint(points_to_orient[1:-1])
                elif captured_dict[1]:
                    # only pdx==1 captured, discard last line point
                    points_to_orient = geo.MultiPoint(points_to_orient[:-1])
                elif captured_dict[-2]:
                    # only pdx==-2 captured, discard first line point
                    points_to_orient = geo.MultiPoint(points_to_orient[1:])
            else:
                raise GeometryError("invalid path given to orient the ring-like line; path must capture a neighbor "
                                    "of the repeated ring end points")

    # for adjusting final index results later
    try:
        lpdx_adjustment: int = {True:1,False:0}[captured_dict[-2]]
    except NameError:
        lpdx_adjustment = 0

    # point capture algorithm
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
                yield lpdx_bag[0]+lpdx_adjustment
            else:
                # not 1 to 1; iterate based on distance to first segment point
                dist_lpdx_sub_list: List[Tuple[float,int]] = []
                seg_point = geo.Point(path_segments[sdx].coords[0])
                lpdx: int
                for lpdx in lpdx_bag:
                    d = seg_point.distance(points_to_orient[lpdx])
                    dist_lpdx_sub_list.append((d,lpdx))
                dist_lpdx_sub_list_sorted = sorted(dist_lpdx_sub_list)
                yield from (lpdx+lpdx_adjustment for _,lpdx in dist_lpdx_sub_list_sorted)


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
                    a_edge = p.boundary.difference(common_edge)
                    # step 4c: make perpendicular segment at midpoint, increase by 1000x length each time until
                    # extends beyond the `x` bounding box; 90 deg rotation means
                    perp_segment = affine.rotate(segment, 90, midpoint)
                    factor = 1000
                    while True:
                        scaled_perp_segment: geo.LineString = affine.scale(perp_segment,factor,factor,factor,midpoint)
                        if scaled_perp_segment.within(p.minimum_rotated_rectangle):
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
