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
def two_triangles():
    t1 = geo.Polygon(((0,0),(1,0),(1,1)))
    t2 = geo.Polygon(((0,0),(0,1),(1,1)))
    return geo.GeometryCollection([t1,t2])

@pytest.fixture
def simple_get_LRsides(monkeypatch):
    f=lambda x,y,z: (x,y)
    monkeypatch.setattr(ops, '_get_LRsides', f)
    return

def test_shapely_fixtures(box, two_triangles, splitter):
    assert shops.split(box, splitter).equals(two_triangles)

def test_splitLR(simple_get_LRsides, box, splitter, two_triangles):
    split = geo.GeometryCollection(list(ops.splitLR(box, splitter)))
    assert split.equals(two_triangles)

def test_get_LRsides(two_triangles, splitter, rev_splitter):
    Left, Right = ops._get_LRsides(*two_triangles, splitter)
    assert Left.equals(two_triangles[1])
    assert Right.equals(two_triangles[0])
    Left, Right = ops._get_LRsides(*two_triangles, rev_splitter)
    assert Left.equals(two_triangles[0])
    assert Right.equals(two_triangles[1])
