# -*- coding: utf-8 -*-

"""Special tools for working with dataclass types."""

from dataclasses import is_dataclass, fields
from typing import Any, Mapping, Callable, Tuple, TypeVar, Dict


def shallow_asdict(obj) -> Dict[str, Any]:
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

def shallow_mapify(o: Any) -> Dict[str, Any]:
    """Shallowly convert an object so it can be unpacked as **kwargs to another context."""
    if isinstance(o, type):
        raise TypeError(f"Cannot turn the class object {o.__name__!s} to a mapping")
    if is_dataclass(o):
        return shallow_asdict(o)
    try:
        return o._asdict()
    except AttributeError:
        pass
    try:
        return o.asdict()
    except AttributeError:
        pass
    try:
        return dict(o)
    except TypeError:
        pass
    try:
        slots = o.__slots__
    except AttributeError:
        pass
    else:
        return dict(zip(slots, (getattr(o, s) for s in slots if hasattr(o, s))))
    try:
        return vars(o)
    except Exception:
        pass
    raise TypeError(f"Failed to turn the class instance of {type(o).__name__!s} to a mapping")

T = TypeVar("T")

def unmapify(d: Mapping, f: Callable[..., T], key_validator: Callable[[Any], bool]=lambda k: True) -> T:
    """Feed a mapping to a function using only validated keys."""
    return f(**{k:v for k,v in d.items() if key_validator(k)})

def field_names(cls_or_instance) -> Tuple[str, ...]:
    """Return a tuple of field names for this dataclass.

    Accepts a dataclass or an instance of one. Tuple elements are of type `dataclasses.Field`."""
    return tuple(f.name for f in fields(cls_or_instance))
