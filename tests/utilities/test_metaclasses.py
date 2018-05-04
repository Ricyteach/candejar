from dataclasses import dataclass

import pytest

from candejar.utilities.metaclasses import SlottedWithDefaultsMeta

@pytest.fixture
def member_descriptor():
    class C:
        __slots__ = "x"
    return type(C.x)

def test_1(member_descriptor):
    class C(metaclass=SlottedWithDefaultsMeta):
        # noinspection PyDataclass
        __slots__ = ("x", "y", "z", "__dict__")

    c = C()

    assert not vars(c)
    assert all(isinstance(getattr(C,slot),member_descriptor) for slot in C.__slots__)

def test_with_dataclasses_1(member_descriptor):
    @dataclass(init=False)
    class C(metaclass=SlottedWithDefaultsMeta):
        # noinspection PyDataclass
        __slots__ = ("x", "y", "z")
        x: int
        y = 1
        z: int = 1

    assert C()
    assert all(isinstance(getattr(C,slot),member_descriptor) for slot in C.__slots__)

def test_with_dataclasses_2(member_descriptor):
    @dataclass
    class C(metaclass=SlottedWithDefaultsMeta):
        # noinspection PyDataclass
        __slots__ = ("x", "y", "z", "__dict__")
        x: int
        y = 1
        z: int = 1

    c = C(2, 2)

    assert not vars(c)
    assert all(isinstance(getattr(C,slot),member_descriptor) for slot in C.__slots__)
