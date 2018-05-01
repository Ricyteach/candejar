# -*- coding: utf-8 -*-

"""Special mixin classes."""

from __future__ import annotations
from typing import Callable, Type, Any, Dict, Optional


class ChildRegistryError(Exception):
    pass

class ChildRegistryMixin:
    """Mixin class that creates classes which track subclasses.

    Each new child class will track its own children.

    Usage example 1:

        class RegisteredByName(ChildRegistryMixin): ...

        assert ChildRegistryMixin._subclasses["RegisteredByName"] is RegisteredByName

    Usage example 2:

        valid_lookup = dict(ClassName="othername")

        class RegisteredByPop(ChildRegistryMixin,
                              make_reg_key=lambda subcls:
                                           valid_lookup.pop(subcls.__name__)):
            pass

        class ClassName(RegisteredByPop): ...

        assert RegisteredByPop._subclasses["othername"] is ClassName

        class InvalidName(RegisteredByPop): ... # <-- ERROR!

    """
    _subclasses: Dict[Any, MixinSubclsType] = dict()
    _make_reg_key: Callable[[AnyType], Any] = lambda subcls: getattr(subcls, "__name__")

    def __init_subclass__(subcls,
                          make_reg_key: Optional[Callable[[AnyType], Any]] = None,
                          key_factory: Optional[Callable[[], Callable[[AnyType], Any]]] = None,
                          **kwargs) -> None:
        # check for invalid argument combo
        if make_reg_key is not None and key_factory is not None:
            raise ChildRegistryError("Detected both a make_reg_key function and a key factory function; "
                                     "only one should be provided")
        super().__init_subclass__(**kwargs)
        # for later child classes of the new class
        subcls._subclasses = dict()
        # child added to the reg of closest parent that is a subclass of CRM
        for parent_cls in subcls.mro()[1:]:
            if issubclass(parent_cls, ChildRegistryMixin):
                break
        else:
            parent_cls = ChildRegistryMixin
        # make the key
        key = parent_cls._make_reg_key(subcls)
        # can't have multiple child classes with same key
        if key not in parent_cls._subclasses:
            parent_cls._subclasses[key] = subcls
        else:
            raise ChildRegistryError(f"Attempted to overwrite the "
                                     f"child class key {key!r} in the "
                                     f"{parent_cls.__name__} registry")
        # set the new class' key maker
        # the subclass' key maker is inherited from parent if a factory or key maker was not provided
        if make_reg_key is not None:
            subcls._make_reg_key = make_reg_key
        if key_factory is not None:
            subcls._make_reg_key = key_factory()
    @classmethod
    def getsubcls(cls, key: Any) -> MixinSubclsType:
        """Get the registered subclass from the key"""
        try:
            return cls._subclasses[key]
        except KeyError:
            raise ChildRegistryError(f"No child class key {key!r} in the "
                                     f"{cls.__name__} subclasses registry")


MixinSubclsType = Type[ChildRegistryMixin]
AnyType = Type[object] # i.e., type


class ChildAsAttributeError(Exception):
    pass

class ChildAsAttributeMixin:
    """Mixin class that adds child classes parent class attributes."""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # the child will be added as a class attribute to the closest parent
        # that is a subclass of CAAB
        for parent_cls in cls.mro()[1:]:
            if issubclass(parent_cls, ChildAsAttributeMixin):
                break
        else:
            parent_cls = ChildAsAttributeMixin
        # can't have multiple child classes with same name
        if cls.__name__ not in vars(parent_cls):
            setattr(parent_cls, cls.__name__, cls)
        else:
            raise ChildAsAttributeError(f"Attempted to overwrite the "
                                        f"{cls.__name__} child class attribute "
                                        f"in the {parent_cls.__name__}.__dict__")

class ClsAttrKeyMakerFactory:
    """Convenience callable object for specifying registration keys defined by ChildRegistry child classes

    The returned key is the class_attr named upon ClsAttrKeyMakerFactory instantiation
    """
    _incomplete = True
    def __init__(self, class_attr):
        self.class_attr = str(class_attr)
    def __set_name__(self, owner, name):
        self.cls = owner
        self._incomplete = False
    def __get__(self, instance, owner):
        if self._incomplete:
            self.cls = owner
            self._incomplete = False
        return self.__call__
    def __call__(self):
        class KeyMaker:
            def __call__(km_self, subcls):
                try:
                    return getattr(subcls, self.class_attr)
                except AttributeError:
                    clsname = self.cls.__name__
                    caller = subcls.__name__
                    raise ChildRegistryError(f"The {clsname} child class {caller} must define a {self.class_attr} attribute")
        return KeyMaker()

