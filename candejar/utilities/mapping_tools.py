# -*- coding: utf-8 -*-

"""Special tools for working with mapping types."""

from typing import Mapping, Iterator, Iterable, TypeVar, Union

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
