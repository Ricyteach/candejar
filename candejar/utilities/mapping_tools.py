# -*- coding: utf-8 -*-

"""Special tools for working with mapping types."""
from types import SimpleNamespace
from typing import Mapping, Iterator, Iterable, TypeVar, Union, Any

T = TypeVar("T")

RECURSION_SENTINEL_TYPE = type("RECURSION_SENTINEL_TYPE", (), {})
RECURSION_SENTINEL = RECURSION_SENTINEL_TYPE()


def lowerify_mapping(obj: T, *, recursive: Union[RECURSION_SENTINEL_TYPE,bool]=RECURSION_SENTINEL) -> T:
    """Take a Mapping and change all the keys to lowercase.

    Use recursive=True to recursively lowerify all objects.
    """
    # no recursion
    if isinstance(obj, Mapping) and (not recursive or recursive is RECURSION_SENTINEL):
        t = tuple((k.lower(),v) for k,v in obj.items())
        obj = type(obj)(t)
    # recursion and a mapping
    elif isinstance(obj, Mapping):
        obj = type(obj)((k.lower(), lowerify_mapping(v, recursive=recursive)) for k, v in obj.items())
    # no recursion argument and not a mapping: error
    elif recursive is RECURSION_SENTINEL:
        raise TypeError(f"Non-mapping {type(obj).__qualname__!r} object detected")
    # recursion and not a mapping
    elif recursive and not isinstance(obj,str) and not isinstance(obj,Iterator) and isinstance(obj,Iterable):
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
