# -*- coding: utf-8 -*-

"""For working with x,y coordinate pairs."""

from typing import Sequence, Mapping, Iterator, Union, TypeVar, Tuple, Any, Generic, Callable, Type, Optional, Iterable

from .exc import GeometryError

class XYCoordMeta(type):
    """Checks an instance for x,y or X,Y attributes."""
    def __instancecheck__(self, instance: Any):
        if hasattr(instance,"x") and hasattr(instance,"y") or\
           hasattr(instance,"X") and hasattr(instance,"Y"):
            return True
        else:
            return False

CoordType = TypeVar("CoordType")

class XYCoords(Generic[CoordType], metaclass=XYCoordMeta):
    """Provides a x,y coordinate pair type for the type checker."""
    x: CoordType
    y: CoordType
    X: CoordType
    Y: CoordType

# for inputs
PointType = Union[Sequence[CoordType], Mapping[str, CoordType], XYCoords[CoordType]]
# for outputs
CoordPair = Tuple[CoordType,CoordType]

class CoordinatesError(GeometryError): ...

def _xy_attrs_case_insensitive(p:XYCoords[CoordType]) -> CoordPair:
    try:
        return p.x, p.y
    except AttributeError as e:
        try:
            return p.X, p.Y
        except AttributeError:
            raise CoordinatesError(f"Coordinates object requires 'x','y' attributes") from e


def _xy_keys_case_insensitive(p:Mapping[str,CoordType]) -> CoordPair:
    try:
        return p['x'], p['y']
    except KeyError as e:
        try:
            return p['X'], p['Y']
        except KeyError:
            raise CoordinatesError(f"Coordinates mapping object requires 'x','y' keys") from e


def _xy_sequence(p:Sequence[CoordType]) -> CoordPair:
    try:
        x, y = p
    except (ValueError, TypeError) as e:
        raise CoordinatesError(f"Coordinates sequence object requires a coordinate pair") from e
    else:
        return x, y


_xy_getter_types: Sequence[Type[PointType]] = (XYCoords, Sequence, Mapping)
_xy_getters: Sequence[Callable[[PointType],CoordPair]] = (_xy_attrs_case_insensitive, _xy_sequence, _xy_keys_case_insensitive)


def get_xy(p: PointType) -> CoordPair:
    getter_keys = (isinstance(p, T) for T in _xy_getter_types)
    try:
        xy_getter = dict(zip(getter_keys, _xy_getters))[True]
    except KeyError:
        if isinstance(p, Iterator):
            raise CoordinatesError(
                f"{type(p).__qualname__} object detected; iterators should not be passed to get_xy function")
        if isinstance(p, str):
            raise CoordinatesError(
                f"{type(p).__qualname__} object detected; str objects should not be passed to get_xy function")
        # not an iterator or string, safe to try unpacking without exhausting
        try:
            x,y = p
        except TypeError:
            raise CoordinatesError(f"{type(p).__qualname__} object detected")
    else:
        try:
            x, y = xy_getter(p)
        except CoordinatesError as e:
            raise CoordinatesError(f"Unable to resolve x,y coordinates from {type(p).__qualname__} object") from e
    try:
        return float(x), float(y)
    except (TypeError, ValueError) as e:
        raise CoordinatesError(f"({type(x).__qualname__!r},{type(y).__qualname__!r}) "
                               f"is not a valid coordinate type pair") from e

def box(p1:PointType, p2:PointType) -> Sequence[CoordPair]:
    x1, y1, x2, y2 = get_xy(p1) + get_xy(p2)
    points = (x1, y1), (x2, y1), (x2, y2), (x1, y2)
    return points

class DrawError(GeometryError): ...

def draw(start: PointType, *, dxdy: Optional[Union[PointType, Iterable[PointType]]]=None):
    x, y = get_xy(start)
    yield x, y
    if dxdy:
        try:
            dx, dy = get_xy(dxdy)
        except CoordinatesError:
            try:
                idxdy = iter(dxdy)
            except TypeError:
                raise DrawError(f"{type(dxdy).__qualname__} dxdy argument detected") from None
            dxs, dys = zip(*(get_xy(p) for p in idxdy))
        else:
            dxs, dys = [dx], [dy]
        for dx, dy in zip(dxs, dys):
            yield from draw((x + dx, y + dy))
            x, y = x + dx, y + dy
