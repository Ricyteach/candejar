import pytest
from candejar.utilities import skip

from typing import List


@pytest.fixture
def SkipList():
    class SkipList(skip.SkippableIterMixin, List):
        @staticmethod
        def skip_f(x):
            return bool(x)
    return SkipList


@pytest.fixture
def SkipAttr_x():
    class SkipAttr_x(skip.SkipAttrIterMixin, List):
        skippable_attr = "x"
    return SkipAttr_x


@pytest.fixture
def sk_lst(SkipList):
    return SkipList([0])


@pytest.fixture
def sk_x(SkipAttr_x):
    Obj = type("Obj", (int, ), {})
    Obj.x = skip.SkipInt(1)
    return SkipAttr_x([Obj(1), Obj(0)])


def test_init(SkipList):
    assert not SkipList()
    assert SkipList([0])
    assert SkipList([1])


def test_len(sk_lst):
    assert len(sk_lst) == 1


def test_iter(sk_lst):
    assert list(sk_lst) == []


def test_skippable_len(sk_lst):
    assert skip.skippable_len(sk_lst) == 0


def test_iter_skippable(sk_lst):
    assert list(skip.iter_skippable(sk_lst)) == [0]


def test_sk_x(sk_x):
    assert len(sk_x) == 2
    assert list(sk_x) == []
    assert skip.skippable_len(sk_x) == 0
    assert list(skip.iter_skippable(sk_x)) == [1, 0]

