# -*- coding: utf-8 -*-

"""For selecting parts of cande problem objects.

Selectable things:
    nodes, elements, boundaries

Selectable bys:
    all:
        number, shape, section_name
    nodes:
        boundary_condition (xcode, ycode), elements
    elements:
        material, step, nodes, boundaries
    boundaries (equivalent to nodes...?):
        boundary_condition (xcode, ycode), nodes, elements

IMPORTANT: attribute errors for individual objects will fail silently
"""

import shapely.geometry as geo
from typing import Sequence, overload, TypeVar, Callable, Any, Iterator, Iterable

from . import exc

T = TypeVar("T")
T_Iterable = Iterable[T]
T_Iterator = Iterator[T]
T_Sequence = Sequence[T]


def copy(selectables: T_Sequence, select_f: Callable[..., T_Iterator], *args, **kwargs) -> T_Sequence:
    if not isinstance(selectables, Sequence):
        raise exc.CandejarTypeError(f"a selectables sequence is required, not {type(selectables).__qualname__}")
    iter_selection = select_f(selectables, *args, **kwargs)
    selection = type(selectables)(iter_selection)
    # preserve nodes reference for new selection (if it exists)
    try:
        nodes = selectables.nodes
    except AttributeError:
        pass
    else:
        selection.nodes = nodes
    return selection


def by_shape(selectables: T_Iterable, shape: geo.base.BaseGeometry) -> T_Iterator:
    selectable_geo = geo.asShape(selectables)
    yield from (s for s,s_geo in zip(selectables, selectable_geo) if shape.contains(s_geo.representative_point()))


def by_filter(selectables: T_Iterable, *, function: Callable[[T], Any]) -> T_Iterator:
    """Basically just a type hinted version of filter (with the arguments swapped)"""
    return filter(function, selectables)


def by_equal_attr(selectable: T, attr: str, value: Any) -> bool:
    # !!!! attribute errors will fail silently !!!!
    no_attr = object()
    return getattr(selectable, attr, no_attr) == value

# a sliceable attribute is one that is an int and can be selected over a range of numbers, e.g. "steps 1 through 3"
# these slices are indexed starting at 1 because that's how CANDE indexes things

@overload
def by_sliceable_attr(selectables: T_Iterable, i: int, *, attr: str) -> T_Iterator: ...

@overload
def by_sliceable_attr(selectables: T_Sequence, s: slice, *, attr: str) -> T_Iterator: ...

def by_sliceable_attr(selectables, x, *, attr):
    if isinstance(x,int):
        function = lambda s: by_equal_attr(s, attr, x)
        return by_filter(selectables, function=function)
    if isinstance(x,slice):
        if x.step is not None and x.step<0:
            raise exc.CandejarValueError(f"negative attribute slice steps are not allowed")
        if x.start is None or x.start==0:
            raise exc.CandejarValueError(f"Candejar attribute slices are indexed at 1; zero index not allowed")
        try:
            selectables_len = len(selectables)
        except TypeError:
            raise exc.CandejarTypeError(f"a selectable sequence is required for slicing")
        yield from (s for v in range(selectables_len+1)[x] for s in by_filter(selectables, function=lambda s: by_equal_attr(s, attr, v)))


@overload
def by_number(selectables: T_Iterable, i: int) -> T_Iterator: ...

@overload
def by_number(selectables: T_Sequence, s: slice) -> T_Iterator: ...

def by_number(selectables, x):
    return by_sliceable_attr(selectables, x, attr="num")


@overload
def by_material(selectables: T_Iterable, i: int) -> T_Iterator: ...

@overload
def by_material(selectables: T_Sequence, s: slice) -> T_Iterator: ...

def by_material(selectables, x):
    return by_sliceable_attr(selectables, x, attr="mat")


@overload
def by_step(selectables: T_Iterable, i: int) -> T_Iterator: ...

@overload
def by_step(selectables: T_Sequence, s: slice) -> T_Iterator: ...

def by_step(selectables, x):
    return by_sliceable_attr(selectables, x, attr="step")
