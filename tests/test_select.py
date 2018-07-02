import pytest

from candejar import select
from dataclasses import make_dataclass

@pytest.fixture
def test_type():
    TestType = make_dataclass("TestType", "mat step".split())
    return TestType

@pytest.fixture
def has_mats_seq(test_type):
    seq = list()
    for i in range(1,4):
        for j in range(i):
            obj = test_type(i, i)
            seq.append(obj)
    return seq

def test_by_material(has_mats_seq):
    x = list(select.by_material(has_mats_seq, 1))
    assert len(x)==1
