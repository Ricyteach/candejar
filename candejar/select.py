# -*- coding: utf-8 -*-

"""For selecting parts of cande problem objects.

Selectable things:
    nodes, elements

Selectable bys:
    both:
        number, shape, collection_name or _key*,
    nodes:
        boundary_condition (xcode, ycode), elements
    elements:
        material, step, nodes
"""

import shapely.geometry as geo
from typing import Sequence, overload, TypeVar, Generic, List, Callable
from types import new_class

T = TypeVar("T")
T_Sequence = new_class("T_Sequence", (Generic[T],Sequence))
T_List = List[T]
A = TypeVar("A")

def by_func(selectables: T_Sequence, *, func: Callable[[T],A]) -> T_List:
    return [s for s in selectables if func(s)]

def by_shape(selectables: T_Sequence, shape: geo.base.BaseGeometry) -> T_List:
    func = lambda s: shape.contains(geo.asShape(s))
    return by_func(selectables, func=func)


@overload
def by_sliceable_attr(selectables: T_Sequence, i: int, *, attr: str) -> T_List: ...

@overload
def by_sliceable_attr(selectables: T_Sequence, s: slice, *, attr: str) -> T_List: ...

def by_sliceable_attr(selectables, x, *, attr):
    if isinstance(x,int):
        func = lambda s: getattr(s, attr) == x
        return by_func(selectables, func=func)
    if isinstance(x,slice):
        return [s for v in range(len(selectables))[x] for s in by_func(selectables, func=lambda s: getattr(s, attr) == v)]


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
