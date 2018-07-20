# -*- coding: utf-8 -*-

"""Special descriptors for working with cande object types."""

from __future__ import annotations
from dataclasses import make_dataclass, field, dataclass
from typing import Any, Type, TypeVar, Generic

from ..exc import CandejarError


T = TypeVar("T")
V = TypeVar("V")


class StandardDescriptor(Generic[T,V]):
    """A typical descriptor.

    The descriptor global default is stored as a StandardDescriptor child class
    attribute but each descriptor instance can have its own default. The
    value associated with each object using the descriptor can be unique.

    The per-object value is stored in the same attribute name as the descriptor
    is assigned at the class level, but preceded with an underscore.
    """
    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "default"):
            raise TypeError(f"StandardDescriptor subclass {cls.__qualname__} requires a default class attribute")

    def __set_name__(self, owner: Type[T], name: str) -> None:
        self.name = name
        self._name = f"_{self.name}"

    def __get__(self, instance: T, owner: Type[T]) -> V:
        while True:
            try:
                return getattr(instance, self._name)
            except AttributeError:
                if instance is None:
                    return self
                else:
                    return self.default

    def __set__(self, instance: T, value: V) -> None:
        setattr(instance, self._name, value)


class AttributeDelegator:
    """Delegates attribute access to another named object attribute."""
    def __init__(self, delegate_name: str) -> None:
        self.delegate_name = delegate_name

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance: Any, owner: Any) -> Any:
        delegate = getattr(instance, self.delegate_name)
        try:
            return getattr(delegate, self.name)
        except AttributeError:
            return self

    def __set__(self, instance: Any, value: Any) -> None:
        delegate = getattr(instance, self.delegate_name)
        setattr(delegate, self.name, value)

class CannedInstanceError(CandejarError, AttributeError):
    pass

class CannedObjects(Generic[T]):
    """A namespace holding references to canned material instances"""
    def __init__(self, child_names):
        self._child_names = child_names
    def __set_name__(self, owner: Type[T], name: str) -> None:
        self._cls: Type[T] = owner
        self._init_incomplete = object() # sentinel for no canned objects yet
    def __get__(self, instance: T, owner: Type[T]) -> CannedObjects:
        # initialize all the instances
        if getattr(self, "_init_incomplete", None):
            for i in self._child_names:
                setattr(self, i, self.get_subclass(i))
            del self._init_incomplete
        return self
    def get_subclass(self, canned_name: str) -> Type[T]:
        """New dataclass with the correct default values for canned material"""
        return make_dataclass(canned_name,
                              [("name", str, field(default=canned_name)),],
                              bases=(self._cls,))
    def __getattr__(self, canned_name: str) -> Any:
        if canned_name in self._child_names:
            raise CannedInstanceError(f"The {type(self).__name__!s} object "
                                           f"{canned_name!s} has not been initialized")
        else:
            raise AttributeError(f"")
