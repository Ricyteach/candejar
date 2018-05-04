from dataclasses import dataclass

from candejar.utilities.metaclasses import SlottedWithDefaultsMeta

def test_1():
    @dataclass(init=False)
    class C(metaclass=SlottedWithDefaultsMeta):
        # noinspection PyDataclass
        __slots__ = ("x", "y", "z")
        x: int
        y = 1
        z: int = 1

    C()

def test_2():
    @dataclass
    class C(metaclass=SlottedWithDefaultsMeta):
        # noinspection PyDataclass
        __slots__ = ("x", "y", "z", "__dict__")
        x: int
        y = 1
        z: int = 1

    C(2,2)
