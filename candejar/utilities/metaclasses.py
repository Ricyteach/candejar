from __future__ import annotations
from typing import Dict, Tuple, Any


class SlottedWithDefaultsMeta(type):
    """
    Example usage #1:

        from dataclasses import dataclass

        @dataclass
        class C(metaclass=SlottedWithDefaultsMeta):
            __slots__ = ("x", "y", "z", "__dict__")
            x: int
            y = 1
            z: int = 1

        C(2)

    Example usage  # 2:

            from dataclasses import dataclass

            @dataclass(init=False)
            class C(metaclass=SlottedWithDefaultsMeta):
                __slots__ = ("x", "y", "z")
                x: int
                y = 1
                z: int = 1

            C()

    """
    def __new__(mcls, name: str, bases: Tuple[type], ns: Dict[str,Any]) -> SlottedWithDefaultsMeta:
        try:
            # preserve original slots object
            slots_object = ns.pop("__slots__")
        except KeyError:
            raise TypeError("__slots__ is required for {mcls.__name__} metaclass")
        # copy namespace WITHOUT slots
        ns_copy = ns.copy()
        # get the slot names
        if isinstance(slots_object, str):
            slot_names = (slots_object,)
        else:
            slot_names = tuple(slots_object)
        # put the slot names back in the namespace for class object instantiation later
        ns["__slots__"] = slot_names
        # remove slots from namespace that also have a value set (would raise an error)
        slots_after = {k: ns.pop(k) for k in ns_copy.keys() if k in ns["__slots__"]}
        # create the class
        cls=super().__new__(mcls, name, bases, ns)
        # set the previously removed class members that conflict with slot names
        for k,v in slots_after.items():
            setattr(cls,k,v)
        # re-assign the slots object
        cls.__slots__ = slots_object
        return cls
