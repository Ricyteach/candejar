# -*- coding: utf-8 -*-

"""Module for items that can be skipped during iteration. The default is for a Skip() instance to be skipped during
iteration but not during any other operation.

Special skippable_len and iter_skippable functions also provided to manage ignoring of skipped items appropriately.
"""

from __future__ import annotations
from .. import exc
from typing import TypeVar, Union, Sequence, ClassVar, Iterator, Generic, Sized, SupportsInt, Iterable


class Skip:
    """Used to mark a field to be skipped during iteration."""
    pass


NOARG = type("NOARGE_TYPE", (), {})()


class SkipInt(Skip, int):
    """Skippable int field."""

    def __new__(cls, x: Union[str, SupportsInt] = NOARG) -> SkipInt:
        if x is NOARG:
            return super().__new__(cls)
        return super().__new__(cls, x)


T = TypeVar('T')
S_co = TypeVar('S', bound='SkippableIterMixin')


class SkippableIterMixin(Generic[T], Sequence[Union[T, Skip]]):
    """Items are skipped during iteration if the inspected field is a subclass of Skip"""

    skippable_attr: ClassVar[str]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, "skippable_attr"):
            raise exc.CandejarTypeError(f"SkippableMixin subclass 'skippable_attr' missing for "
                                        f"{type(self).__qualname__} object ")

    def __iter__(self) -> Iterator[T]:
        yield from (i for i in super().__iter__() if not isinstance(getattr(i, self.skippable_attr), Skip))


def skippable_len(x: Union[Sized, SkippableIterMixin[T]]) -> int:
    """Same as len() but takes into account items marked to be skipped."""
    if isinstance(x, SkippableIterMixin):
        return sum(1 for _  in x)
    return len(x)


def iter_skippable(x: Iterable[Union[T, Skip]]) -> Iterator[Union[T, Skip]]:
    """Same as iter() but does NOT skip over Skip() instances."""
    if isinstance(x, SkippableIterMixin):
        x: SkippableIterMixin
        return super(SkippableIterMixin, x).__iter__()
    return iter(x)
