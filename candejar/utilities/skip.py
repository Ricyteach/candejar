# -*- coding: utf-8 -*-

"""Module for items that can be skipped during iteration. Special skippable_len
function also provided to give length while ignoring skipped items."""

from __future__ import annotations
from .. import exc
from typing import TypeVar, Union, Sequence, ClassVar, Iterator, Generic, Sized


class Skip:
    """Used to mark a field to be skipped during iteration."""
    pass


class SkipInt(Skip, int):
    """Skippable int field (zero)."""

    def __new__(cls) -> Skip:
        return super().__new__(cls)


T = TypeVar('T')
S_co = TypeVar('S', bound='SkippableIterMixin')


class SkippableIterMixin(Generic[T], Sequence[Union[T, Skip]]):
    """Items are skipped during iteration if the inspected field
    is a subclass of Skip"""

    skippable_attr: ClassVar[str]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(cls)
        if not hasattr(cls, "skippable_attr"):
            raise exc.CandejarTypeError(f"'skippable_attr' missing for "
                                        f"SkippableMixin subclass "
                                        f"{cls.__qualname__}")

    """ 
    @overload
    def __getitem__(self, i: int) -> Union[T, Skip]:
        ...

    @overload
    def __getitem__(self, s: slice) -> S_co[Union[T, Skip]]:
        ...

    def __getitem__(self, x):
        result = super().__getitem__(x)

        if isinstance(x, slice):
            return result

        try:
            attr_value = getattr(result, self.skippable_attr)
        except AttributeError:
            raise exc.CandeAttributeError(f"{type(result).__qualname__} missing "
                                          f"skippable attribute "
                                          f"{self.skippable_attr!r}")

        if not isinstance(attr_value, Skip):
            return result
        raise exc.CandeIndexError(f"{type(self).__qualname__} index out of range for non-skipped items")

    """

    def __iter__(self) -> Iterator[T]:
        yield from (i for i in super().__iter__()
                    if not isinstance(getattr(i, self.skippable_attr, None), Skip))


def skippable_len(x: Union[Sized, SkippableIterMixin[T]]) -> int:
    if isinstance(x, SkippableIterMixin):
        return sum(1 for _  in x)
    return len(x)
