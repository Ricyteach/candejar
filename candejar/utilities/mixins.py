# -*- coding: utf-8 -*-

"""Special mixin classes."""

from __future__ import annotations
from typing import Callable, Type, Any, Dict, Optional, Counter


class ChildRegistryError(Exception):
    pass

class ChildRegistryMixin:
    """Mixin class that creates classes which track subclasses.

    Each new child class will track its own children.

    Usage example 1:

        class RegisteredByName(ChildRegistryMixin): ...

        assert ChildRegistryMixin.getsubcls("RegisteredByName") is RegisteredByName

    Usage example 2:

        valid_lookup = dict(ClassName="othername")

        class RegisteredByPop(ChildRegistryMixin,
                              make_reg_key=lambda subcls:
                                           valid_lookup.pop(subcls.__name__)):
            pass

        class ClassName(RegisteredByPop): ...

        assert RegisteredByPop.getsubcls("othername") is ClassName

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
            raise ChildRegistryError("Detected both a make_reg_key function and "
                                     "a key factory function; only one should "
                                     "be provided")
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

_CHILD_DISPATCHER_METHODS= """
def __new__(cls, {arg1!s}, *args, **kwargs):
    if cls is WrappedCls:
        # dispatch to a registered child class
        subcls = cls.getsubcls({arg1!s})
        return super(WrappedCls, subcls).__new__(subcls)
    else:
        return super(WrappedCls, cls).__new__(cls)
def __init_subclass__(subcls, **kwargs):
    super(WrappedCls, subcls).__init_subclass__(**kwargs)
    # add __new__ contructor to child class based on default first argument
    def __new__(cls, {arg1!s}: str = subcls.{arg1!s}, *args, **kwargs):
        s = super(WrappedCls,cls).__new__(cls, *args, **kwargs)
        return s
    subcls.__new__ = __new__"""[1:]


def child_dispatcher(keyname):
    """A decorator to allow classes to dispatch instantiation to registered child classes

    The decorated class must have a `getsubcls` method in the form of `Callable[[Any], Type[WrappedCls]]` and a child
    class registered under the decorated class `keyname` and matching first argument
    """
    def decorator(WrappedCls):
        ns=dict(WrappedCls=WrappedCls)
        code=_CHILD_DISPATCHER_METHODS.format(arg1 = str(keyname))
        exec(code,ns,ns)
        __new__ = ns["__new__"]
        __init_subclass__ = ns["__init_subclass__"]
        WrappedCls.__new__ = __new__
        WrappedCls.__init_subclass__ = classmethod(__init_subclass__)
        return WrappedCls
    return decorator

class CompositeAttributeError(AttributeError):
    pass

class Composite(ChildRegistryMixin):
    @property
    def _component_attrs(self):
        return [attr for comp in self.components for attr in vars(comp)]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.components = []
    def __getattr__(self, item):
        ctr = Counter(self._component_attrs)
        if any(v!=1 for v in ctr.values()):
            dupes = [k for k,v in ctr.items() if v!=1]
            comps = [c for c in self.components if any(dupeattr in vars(c) for dupeattr in dupes)]
            raise CompositeAttributeError(f"Duplicate attribute names {str(dupes)[1:-1]} detected "
                                          f"in components {str(comps)[1:-1]}")
        try:
            comp = next(c for c in self.components if hasattr(c,item))
            return getattr(comp, item)
        except (StopIteration, AttributeError):
            raise AttributeError("{type(self)!r} object has no attribute {item!r}") from None
    def add_component(self, comp):
        self.components.append(comp)
