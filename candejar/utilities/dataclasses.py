# -*- coding: utf-8 -*-

"""Special tools for working with dataclass types."""

from dataclasses import is_dataclass, fields
from typing import Any, Mapping, Callable, Tuple


def shallow_asdict(obj):
    """Shallowly return the fields of a dataclass instance as a new dictionary mapping
    field names to field values."""
    if not isinstance(obj, type) and is_dataclass(obj):
        result = []
        for f in fields(obj):
            value = getattr(obj, f.name)
            result.append((f.name, value))
        return dict(result)
    else:
        raise TypeError("shallow_asdict() should be called on dataclass instances")

def shallow_mapify(o: Any) -> Mapping:
    """Shallowly onvert an object so it can be unpacked as **kwargs to another context."""
    if isinstance(o, type):
        raise TypeError("Received command to turn the class instance of {o.__name__!s} to a mapping")
    if is_dataclass(o):
        return shallow_asdict(o)
    elif isinstance(o, Mapping):
        return o
    else:
        return vars(o)

def unmapify(d: Mapping, f: Callable, key_validator: Callable[[Any], bool]=lambda k: True):
    """Feed a mapping to a function using only validated keys."""
    return f(**{k:v for k,v in d.items() if key_validator(k)})

def field_names(cls_or_instance) -> Tuple[str, ...]:
    """Return a tuple of field names for this dataclass.

    Accepts a dataclass or an instance of one. Tuple elements are of type `dataclasses.Field`."""
    return tuple(f.name for f in fields(cls_or_instance))
