import pytest

from candejar.geometry import box,draw

def test_box():
    extents = box((-445.140000, -132.380000), (445.140000, 160.910000))
    extents_coords = tuple(c for pair in extents for c in pair)
    point_coords = -445.140000, -132.380000, 445.140000, -132.380000, 445.140000, 160.910000, -445.140000, 160.910000
    assert extents_coords == pytest.approx(point_coords)

def test_draw():
    layers_gen = draw((-103.900000, -6.380000), dxdy=((103.140000 - -103.900000, 0),
                                                      (270.430000 - 103.140000, 160.910000 - -6.380000),
                                                      (-271.190000 - 270.430000, 0),))
    layer_coords_gen = (c for pair in layers_gen for c in pair)
    point_coords = -103.900000, -6.380000, 103.140000, -6.380000, 270.430000, 160.910000, -271.190000, 160.910000
    assert tuple(layer_coords_gen) == pytest.approx(point_coords)
