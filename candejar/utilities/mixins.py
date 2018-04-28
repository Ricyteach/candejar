# -*- coding: utf-8 -*-

"""Special mixin classes."""

class ChildRegistryError(Exception):
    pass

class ChildRegistryBase:
    """Mixin class that creates classes which track subclasses.

    Each new child class will track its own children.
    """
    # for direct child classes of CRB
    subclasses = dict()
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # for child classes of the new class
        cls.subclasses = dict()
        # the child will be added to the registry of the closest parent that is a subclass of CRB
        for parent_cls in cls.mro()[1:]:
            if issubclass(parent_cls, ChildRegistryBase):
                break
        else:
            parent_cls = ChildRegistryBase
        # can't have multiple child classes with same name
        if cls.__name__ not in parent_cls.subclasses:
            parent_cls.subclasses[cls.__name__] = cls
        else:
            raise ChildRegistryError(f"Attempted to overwrite the "
                                     f"{cls.__name__} child class in the "
                                     f"{parent_cls.__name__} registry")
