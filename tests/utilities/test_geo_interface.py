import pytest
from dataclasses import dataclass
from typing import List
from shapely import geometry as geo

from candejar.utilities.mixins import GeoMixin, GeoInterfaceError


def test_no_geo_type():
    with pytest.raises(GeoInterfaceError):
        class C(GeoMixin): ...


@pytest.fixture
def point_cls():
    @dataclass
    class P(GeoMixin, geo_type="Point"):
        x: float
        y: float
    return P


@pytest.fixture
def multipoint_cls():
    class MP(GeoMixin, List, geo_type="MultiPoint"):
        pass
    return MP


@pytest.fixture
def polygon_cls(point_cls):
    mp = [point_cls(0,0), point_cls(1,0), point_cls(1,1),
         point_cls(1, 1), point_cls(2, 1), point_cls(2, 2)]
    @dataclass
    class Poly(GeoMixin, geo_type="Polygon"):
        i: int
        j: int
        k: int
        l: int = 0
        nodes = mp
    return Poly


@pytest.fixture
def multipolygon_cls(point_cls):
    mp = [point_cls(0,0), point_cls(1,0), point_cls(1,1),
         point_cls(1, 1), point_cls(2, 1), point_cls(2, 2)]
    class MPoly(GeoMixin, List, geo_type="MultiPolygon"):
        nodes = mp
    return MPoly


def test_point_cls(point_cls):
    assert geo.asShape(point_cls(0,0))


def test_polygon_cls(polygon_cls):
    assert geo.asShape(polygon_cls(1, 2, 3))


def test_multipoint_cls(multipoint_cls, point_cls):
    assert geo.asShape(multipoint_cls([point_cls(0,0), point_cls(1,1)]))


def test_multipolygon_cls(multipolygon_cls, polygon_cls):
    polygon_seq = [polygon_cls(1, 2, 3), polygon_cls(4, 5, 6)]
    mpoly = multipolygon_cls(polygon_seq)
    assert geo.asShape(mpoly)
