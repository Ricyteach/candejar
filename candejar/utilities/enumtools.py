# -*- coding: utf-8 -*-

"""Module for useful enum.Enum related tools."""

from enum import Enum
from functools import wraps
from typing import Callable, Any


class EnumToolsError(Exception):
    pass

class CapitalizedEnumError(EnumToolsError):
    pass

class CapitalizedEnumMixin(Enum):
    def __new__(cls, s, *args, **kwargs):
        try:
            if s != s.capitalize():
                raise CapitalizedEnumError("use {s.capitalize!r} instead?")
        except AttributeError:
            raise CapitalizedEnumError("string expected for s argument, not {type(s).__name__}")
        return super().__new__(cls, s, *args, **kwargs)

def callable_enum_dispatcher(*, dispatch_func: Callable[[Any], Any]):
    """Makes enum members callable and sends arguments to the supplied dispatch function"""
    def enum_decorator(EnumCls):
        if not issubclass(EnumCls, Enum):
            raise EnumToolsError(f"Decorator must be used on Enum subclass, not {EnumCls.__name__}")
        def __call__(self, *args, **kwargs):
            callable = dispatch_func(self.value)
            return callable(*args, **kwargs)
        @property
        def callable(self):
            return dispatch_func(self.value)
        EnumCls.__call__ = __call__
        EnumCls.callable = callable
        return EnumCls
    return enum_decorator
