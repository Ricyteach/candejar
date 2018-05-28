# -*- coding: utf-8 -*-

"""Operations for working with geometries."""

import pytest
import shapely.geometry as geo
import shapely.ops as shops

from candejar.geometry import ops


@pytest.fixture
def box():
    return geo.box(0,0,1,1)

@pytest.fixture
def splitter():
    return geo.LineString(((-1,-1),(2,2)))

@pytest.fixture
def rev_splitter(splitter):
    return geo.LineString(reversed(list(splitter.coords)))

@pytest.fixture
def two_points_to_orient():
    return geo.LineString(((0,0),(1,1)))

@pytest.fixture
def four_points_to_orient():
    return geo.LineString(((0,0),(1,0),(1,1),(0,0)))

@pytest.fixture
def two_triangles():
    t1 = geo.Polygon(((0,0),(1,0),(1,1)))
    t2 = geo.Polygon(((0,0),(0,1),(1,1)))
    return geo.GeometryCollection([t1,t2])

@pytest.fixture
def do_patch_get_LRsides(monkeypatch):
    f=lambda x,y,z: (x,y)
    monkeypatch.setattr(ops, 'get_LRsides', f)
    return

@pytest.fixture
def line_coords():
    return [(0, 0), (0, 0), (1, 1), (2, 2)]

@pytest.fixture
def line(line_coords):
    return geo.LineString(line_coords)

def test_shapely_fixtures(box, two_triangles, splitter):
    assert shops.split(box, splitter).equals(two_triangles)

def test_iter_segments(line, line_coords):
    strings = list(ops.iter_segments(line))
    assert len(strings) == 3
    assert line_coords[:-1] == [list(s.coords)[0] for s in strings]
    assert line_coords[1:] == [list(s.coords)[1] for s in strings]

def test_iter_oriented_line_pt_idx(splitter, rev_splitter, two_points_to_orient):
    idxs_list = list(ops.iter_oriented_line_pt_idx(two_points_to_orient, splitter))
    assert idxs_list==[0,1]
    idxs_list_rev = list(ops.iter_oriented_line_pt_idx(two_points_to_orient, rev_splitter))
    assert idxs_list_rev==[1,0]

def test_iter_oriented_line_pt_idx_hard(splitter, rev_splitter, four_points_to_orient):
    idxs_list = list(ops.iter_oriented_line_pt_idx(four_points_to_orient, splitter))
    assert idxs_list==[3,2,0]
    idxs_list_rev = list(ops.iter_oriented_line_pt_idx(four_points_to_orient, rev_splitter))
    assert idxs_list_rev==[0,2,3]

def test_splitLR(do_patch_get_LRsides, box, splitter, two_triangles):
    split = geo.GeometryCollection(list(ops.splitLR(box, splitter)))
    assert split.equals(two_triangles)

def test_splitLR_(box, splitter, two_triangles):
    split = geo.GeometryCollection(list(ops.splitLR_(box, splitter)))
    assert split.equals(two_triangles)

def test_get_LRsides(two_triangles, splitter, rev_splitter):
    Left, Right = ops.get_LRsides(*two_triangles, splitter)
    assert Left.equals(two_triangles[1])
    assert Right.equals(two_triangles[0])
    Left, Right = ops.get_LRsides(*two_triangles, rev_splitter)
    assert Left.equals(two_triangles[0])
    assert Right.equals(two_triangles[1])
