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
        """A list with a x skippable attribute."""
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
    """a SkipList should be instantiated same as a regular list"""
    assert not SkipList()
    assert SkipList([0])
    assert SkipList([1])


def test_len(sk_lst):
    """length of sk_lst should include skippable items"""
    assert len(sk_lst) == 1


def test_iter(sk_lst):
    """regular iteration should skip the skippable items"""
    assert list(sk_lst) == []


def test_skippable_len(sk_lst):
    """skippable_len should ignore skippable items"""
    assert skip.skippable_len(sk_lst) == 0


def test_iter_skippable(sk_lst):
    """iter_skippable should NOT skip the skippable items"""
    assert list(skip.iter_skippable(sk_lst)) == [0]


def test_sk_x(sk_x):
    """Various tests for a SkipAttrIterMixin with a check for skippable marker in 'x'"""
    assert len(sk_x) == 2  # len should work as normal
    assert list(sk_x) == []  # iteration should skip items with a skippable attribute
    assert skip.skippable_len(sk_x) == 0  # special len function also ignores items with skippable attribute
    assert list(skip.iter_skippable(sk_x)) == [1, 0]  # special iteration includes skippables

