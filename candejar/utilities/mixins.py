# -*- coding: utf-8 -*-

"""Special mixin classes."""

class ChildRegistryBase:
    """Mixin class that tracks subclasses."""
    subclasses = {}
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.__name__] = cls
