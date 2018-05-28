import pytest

from candejar.utilities.sequence_tools import orient_seq, dedupe, iter_distances, nn_mapping, iter_nn

def test_orient_seq():
    x = list("abcdefg")
    y = list(reversed(x))
    x_orient = [3,4,5]
    y_orient = list(reversed(x_orient))
    bad_orient = [3,5,4]
    negative_idx = [3,4,-5]
    invalid_idx = [3,4,5,6,7,8,9,10,11,12,13,14,15]
    assert x==orient_seq(x, x_orient)
    assert y==orient_seq(x, y_orient)
    with pytest.raises(ValueError):
        orient_seq(x, bad_orient)
    with pytest.raises(ValueError):
        orient_seq(x, negative_idx)
    with pytest.raises(IndexError):
        orient_seq(x, invalid_idx)

def test_dedupe():
    x = list("aaab")
    assert dedupe(x)==list("ab")

def test_iter_distances():
    item = 0
    seq = [-2,0,3,6,12]
    distances = list(iter_distances(item, seq))
    assert seq==distances
