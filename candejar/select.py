# -*- coding: utf-8 -*-

"""For selecting parts of cande problem objects.

Selectable things:
    nodes, elements, boundaries

Selectable bys:
    all:
        number, shape, collection_name or _key*,
    nodes:
        boundary_condition (xcode, ycode), elements
    elements:
        material, step, nodes, boundaries
    boundaries (equivalent to nodes...?):
        boundary_condition (xcode, ycode), nodes, elements
"""

import shapely.geometry as geo
from typing import Sequence, overload, TypeVar, Generic, List, Callable, Any
from types import new_class

T = TypeVar("T")
T_Sequence = new_class("T_Sequence", (Generic[T],Sequence))
T_List = List[T]

def by_filter(selectables: T_Sequence, *, function: Callable[[T], Any]) -> T_List:
    return list(filter(function, selectables))

def by_shape(selectables: T_Sequence, shape: geo.base.BaseGeometry) -> T_List:
    function = lambda s: shape.contains(geo.asShape(s))
    return by_filter(selectables, function=function)


@overload
def by_sliceable_attr(selectables: T_Sequence, i: int, *, attr: str) -> T_List: ...

@overload
def by_sliceable_attr(selectables: T_Sequence, s: slice, *, attr: str) -> T_List: ...

def by_sliceable_attr(selectables, x, *, attr):
    if isinstance(x,int):
        function = lambda s: getattr(s, attr) == x
        return by_filter(selectables, function=function)
    if isinstance(x,slice):
        return [s for v in range(len(selectables))[x] for s in by_filter(selectables, function=lambda s: getattr(s, attr) == v)]


@overload
def by_number(selectables: T_Sequence, i: int) -> T_List: ...

@overload
def by_number(selectables: T_Sequence, s: slice) -> T_List: ...

def by_number(selectables, x):
    return by_sliceable_attr(selectables, x, attr="num")


@overload
def by_material(selectables: T_Sequence, i: int) -> T_List: ...

@overload
def by_material(selectables: T_Sequence, s: slice) -> T_List: ...

def by_material(selectables, x):
    return by_sliceable_attr(selectables, x, attr="mat")


@overload
def by_step(selectables: T_Sequence, i: int) -> T_List: ...

@overload
def by_step(selectables: T_Sequence, s: slice) -> T_List: ...

def by_step(selectables, x):
    return by_sliceable_attr(selectables, x, attr="step")
