import pytest
from candejar.utilities import skip

from typing import List


@pytest.fixture
def C():
    class SkipList(skip.SkippableIterMixin, List):
        skippable_attr = "num"
    return SkipList


def test_init(C):
    assert C([1])
