# -*- coding: utf-8 -*-

"""Special tools for working with mapping types."""
from types import SimpleNamespace
from typing import Mapping, Iterator, Iterable, TypeVar, Union, Any

T = TypeVar("T")

T_Sentinel = type("T_Sentinel", (), {})
R_SENTINEL = T_Sentinel()
T_Bool = Union[T_Sentinel, bool]


def lowerify_mapping(obj: T, *, recursive: T_Bool=R_SENTINEL) -> T:
    """Take a Mapping and change all the keys to lowercase.

    Use recursive=True to recursively lowerify all objects.
    """
    if isinstance(obj, Mapping) and (not recursive or recursive is R_SENTINEL):
        # no recursion
        gen = ((k.lower(),v) for k,v in obj.items())
        obj = type(obj)(gen)
    elif isinstance(obj, Mapping):
        # recursion and a mapping
        obj = type(obj)((k.lower(), lowerify_mapping(v, recursive=recursive)) for k, v in obj.items())
    elif recursive is R_SENTINEL:
        # no recursion argument and not a mapping: error
        raise TypeError(f"Non-mapping {type(obj).__qualname__!r} object detected")
    elif recursive and not isinstance(obj,str) and not isinstance(obj,Iterator) and isinstance(obj,Iterable):
        # recursion and not a mapping
        obj = type(obj)(lowerify_mapping(i, recursive=True) for i in obj)
    return obj


def shallow_mapify(o: Any) -> Mapping[str, Any]:
    """Shallowly convert an object so it can be unpacked as **kwargs to another context."""
    if isinstance(o, Mapping):
        return o
    if isinstance(o, type):
        raise TypeError(f"Cannot mapify the class object {o.__qualname__}")
    if hasattr(o, '__dataclass_fields__'):
        from .dataclasses import shallow_asdict
        return shallow_asdict(o)
    if isinstance(o, SimpleNamespace):
        return vars(o)
    # attempt common as dict methods
    as_dicts = (getattr(o,n,None) for n in "_asdict asdict as_dict _as_dict".split())
    for asdict in (a for a in as_dicts if a is not None):
        if isinstance(asdict, Mapping):
            m = asdict
        else:
            m = asdict()
        if isinstance(m, Mapping):
            return m
    try:
        return dict(o)
    except (TypeError, ValueError):
        pass
    raise TypeError(f"Failed to mapify {type(o).__qualname__} object")
