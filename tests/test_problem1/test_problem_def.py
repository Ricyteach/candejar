import shapely.geometry as geo
import shapely.ops as ops
import pytest

from candejar.geometry import box, draw, get_xy, splitLR

def test_problem_geometry():
    extents = box((-445.140000, -132.380000), (445.140000, 160.910000))
    extents = geo.Polygon(extents)
    layers = tuple(draw((-103.900000,-6.380000),dxdy=((103.140000--103.900000, 0),
                                                (270.430000-103.140000, 160.910000--6.380000),
                                                (-271.190000-270.430000, 0),)))
    layers_p = geo.Polygon(layers)
    select_backfill = geo.Polygon(box((-103.900000,-6.380000),(103.140000,142.910000)))
    insitu = extents.difference(layers_p)
    other_backfill = layers_p.difference(select_backfill)

    mat_seq=(insitu, other_backfill, select_backfill)
    geo.MultiPolygon(mat_seq)

    layer_strings = (((-1000,0.100000),(-103.900000,0.100000),(-67.900000,0.100000),(-67.900000,9.310000),(-57.170000,0.100000),(-45.890000,0.130000),(-34.610000,0.120000),(-23.330000,0.110000),(-12.050000,0.060000),(0,0),(10.520000,-0.050000),(21.800000,-0.100000),(33.080000,-0.160000),(44.360000,-0.260000),(55.640000,-0.380000),(66.630000,8.790000),(66.630000,-0.380000),(103.140000,-0.380000),(1000,-0.380000)),
                       ((-1000,12.100000),(-103.900000,12.100000),(-82.900000,12.100000),(-67.900000,9.310000),(66.630000,8.790000),(81.630000,11.620000),(103.140000,11.620000),(1000,11.620000)),
                       ((-1000,24.100000),(-103.900000,24.100000),(-67.650000,24.100000),(66.620000,23.620000),(103.140000,23.620000),(1000,23.620000)),
                       ((-1000,36.100000),(-103.900000,36.100000),(-67.430000,36.100000),(66.650000,35.620000),(103.140000,35.620000),(1000,35.620000)),
                       ((-1000,48.100000),(-103.900000,48.100000),(-67.290000,48.100000),(66.680000,47.620000),(103.140000,47.620000),(1000,47.620000)),
                       ((-1000,60.100000),(-103.900000,60.100000),(-67.130000,60.100000),(66.730000,59.620000),(103.140000,59.620000),(1000,59.620000)),
                       ((-1000,72.100000),(-103.900000,72.100000),(-66.960000,72.100000),(66.800000,71.620000),(103.140000,71.620000),(1000,71.620000)),
                       ((-1000,84.100000),(-103.900000,84.100000),(-66.750000,84.100000),(66.860000,83.620000),(103.140000,83.620000),(1000,83.620000)),
                       ((-1000,96.100000),(-103.900000,96.100000),(-66.550000,96.100000),(66.920000,95.620000),(103.140000,95.620000),(1000,95.620000)),
                       ((-1000,108.100000),(-103.900000,108.100000),(-66.420000,108.100000),(67.010000,107.620000),(103.140000,107.620000),(1000,107.620000)),
                       ((-1000,122.230000),(-103.900000,122.230000),(-82.900000,122.230000),(-66.360000,121.850000),(67.140000,120.970000),(81.630000,119.620000),(103.140000,119.620000),(1000,119.620000)),
                       ((-1000,130.910000),(-103.900000,130.910000),(-55.400000,130.910000),(-44.240000,130.600000),(-33.070000,130.310000),(-21.900000,130.070000),(-10.730000,129.920000),(0,129.810000),(11.600000,129.740000),(22.770000,129.770000),(33.940000,129.840000),(45.110000,129.950000),(56.280000,130.120000),(103.140000,130.120000),(1000,130.120000)),
                       ((-1000,142.910000),(-103.900000,142.910000),(0,142.910000),(103.140000,142.910000),(1000,142.910000)),
                       ((-1000,151.910000),(-103.900000,151.910000),(0,151.910000),(103.140000,151.910000),(1000,151.910000)),
                      )

    split_polygons = [layers_p]
    layer_strings = geo.MultiLineString([geo.LineString(l) for l in layer_strings])
    geo.GeometryCollection([layer_strings, insitu, other_backfill, select_backfill])

    layer_multi_polygons = []
    for layer_string in (geo.LineString(l) for l in layer_strings):
        lhs = []
        rhs = []
        for split_polygon in split_polygons:
            layer_string = ops.snap(layer_string, split_polygon, 0.1)
            left, right = splitLR(split_polygon, layer_string)
            lhs.extend(list(left))
            rhs.extend(list(right))
        split_polygons = lhs
        layer_multi_polygons.append(geo.MultiPolygon(rhs))
    layer_multi_polygons.append(geo.MultiPolygon(lhs))
    layer1 = insitu.union(layer_multi_polygons[0])
    layer1 = layer1 if hasattr(layer1, "__iter__") else geo.MultiPolygon([layer1])
    layer_multi_polygons = [layer1, *layer_multi_polygons[1:]]
    geo.MultiPolygon([p for p_set in layer_multi_polygons for p in p_set])

    assert len(layer_multi_polygons)==15

def test_problem_structure():
    n_box_elements = 42
    box_el_nums = range(1,n_box_elements+1)
    box_group_boundaries = [10, 11, 21, 22, 31, 32, 42, n_box_elements+1]
    box_element_group_nums = {}
    ibounds=iter(enumerate(box_group_boundaries,1))
    grp_num,b = next(ibounds)
    for el_num in box_el_nums:
        if el_num==b:
            grp_num,b = next(ibounds)
        box_element_group_nums[el_num] = grp_num
    assert len(box_element_group_nums) == n_box_elements
