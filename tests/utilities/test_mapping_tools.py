from candejar.utilities.mapping_tools import lowerify_mapping

def test_lowerify_mapping():
    iterator = iter(dict(X=1, y=2))
    d1 = dict(a=iterator, b=(1,2,3), C="abc", X=1, y=2, z=dict(X=1, y=2, Z=3))
    d2 = dict(a=iterator, b=(1,2,3), c="abc", x=1, y=2, z=dict(X=1, y=2, Z=3))
    d3 = dict(a=iterator, b=(1,2,3), c="abc", x=1, y=2, z=dict(x=1, y=2, z=3))
    assert lowerify_mapping(d1)== d2
    assert lowerify_mapping(d1, recursive=True) == d3
    # make sure iterator not exhausted
    assert list(iterator) == ["X", "y"]
