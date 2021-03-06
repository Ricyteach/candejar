# -*- coding: utf-8 -*-

"""Special mixin classes."""

from __future__ import annotations
from typing import Callable, Any, Dict, Optional, Counter, TypeVar, Generic, \
    Type, Sequence, NamedTuple, ClassVar


class ChildRegistryError(Exception):
    pass


MixinSubcls = TypeVar("MixinSubcls", bound="ChildRegistryMixin")
MixinSubclsChild = TypeVar("MixinSubclsChild", bound=MixinSubcls)


class ChildRegistryMixin(Generic[MixinSubcls]):
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
    _subclasses: Dict[Any, Type[ChildRegistryMixin]] = dict()
    _make_reg_key: Callable[[type], Any] = lambda subcls: getattr(subcls, "__name__")

    def __init_subclass__(subcls,
                          make_reg_key: Optional[Callable[[type], Any]] = None,
                          key_factory: Optional[Callable[[], Callable[[type], Any]]] = None,
                          **kwargs) -> None:
        # check for invalid argument combo
        if make_reg_key is not None and key_factory is not None:
            raise ChildRegistryError("Detected both a make_reg_key function and "
                                     "a key factory function; only one should "
                                     "be provided")
        super().__init_subclass__(**kwargs)
        # for later child classes of the new class
        subcls._subclasses: Dict[Any, Type[MixinSubcls]] = dict()
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
                                     f"{parent_cls.__qualname__} registry")
        # set the new class' key maker
        # the subclass' key maker is inherited from parent if a factory or key maker was not provided
        if make_reg_key is not None:
            subcls._make_reg_key = make_reg_key
        if key_factory is not None:
            subcls._make_reg_key = key_factory()

    @classmethod
    def getsubcls(cls: Type[MixinSubcls], key: Any) -> Type[MixinSubclsChild]:
        """Get the registered subclass from the key"""
        try:
            return cls._subclasses[key]
        except KeyError:
            raise ChildRegistryError(f"No child class key {key!r} in the "
                                     f"{cls.__name__} subclasses registry")


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
                    raise ChildRegistryError(
                        f"The {clsname} child class {caller} must define a {self.class_attr} attribute")

        return KeyMaker()


_CHILD_DISPATCHER_METHODS = """
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
        ns = dict(WrappedCls=WrappedCls)
        code = _CHILD_DISPATCHER_METHODS.format(arg1=str(keyname))
        exec(code, ns, ns)
        __new__ = ns["__new__"]
        __init_subclass__ = ns["__init_subclass__"]
        WrappedCls.__new__ = __new__
        WrappedCls.__init_subclass__ = classmethod(__init_subclass__)
        return WrappedCls

    return decorator


class CompositeAttributeError(AttributeError):
    pass


class CompositeMixin:
    @property
    def _component_attrs(self):
        return [attr for comp in self.components for attr in vars(comp)]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.components = []

    def __getattr__(self, item):
        ctr = Counter(self._component_attrs)
        if any(v != 1 for v in ctr.values()):
            dupes = [k for k, v in ctr.items() if v != 1]
            comps = [c for c in self.components if any(dupeattr in vars(c) for dupeattr in dupes)]
            raise CompositeAttributeError(f"Duplicate attribute names {str(dupes)[1:-1]} detected "
                                          f"in components {str(comps)[1:-1]}")
        try:
            comp = next(c for c in self.components if hasattr(c, item))
            return getattr(comp, item)
        except (StopIteration, AttributeError):
            raise AttributeError("{type(self)!r} object has no attribute {item!r}") from None

    def add_component(self, comp):
        self.components.append(comp)


##########################################################################
#                        GeoJSON interface Mixin                         #
##########################################################################

class GeoInterfaceError(Exception):
    pass


class GeoTuple(NamedTuple):
    type: str
    coords: Sequence


class GeoInterface:
    """A descriptor that returns the __geo_interface__ representation of various geometric objects

    The geo_type argument specifies the type of geometry. Choices are:
        - Point, MultiPoint, Polygon, LineString, MultiPolygon, MultiLineString, and Node*
        - Point coordinates are specified as pt.x and pt.y
        - Polygon points are specified as p.i, p.j, p.k, and (optional) p.l
        - LineString points are specified as p.i and p.j
        - By default a Polygon with only 2 valid points (i, j) will delegate to a LineString instead

    * Node not part of GeoJSON format spec; a Node contains a node.node attribute which specifies the point number
      TODO: Node could be reworked later to be a "Feature" containing a Point instead but don't have time for that now
    """

    def __init__(self, geo_type, strict=False):
        self.geo_type = geo_type
        self.strict = strict

    def __get__(self, instance, owner):
        if instance is not None:
            _f = self._lookup[self.geo_type]
            try:
                geo_type, coords = _f(self, instance)
            except Exception as e:
                raise GeoInterfaceError(f"{type(instance).__qualname__} object") from e
            return dict(type=geo_type, coordinates=coords)
        return self

    def point(self, node):
        """A GeoTuple for Point representation."""
        return GeoTuple("Point", [node.x, node.y])

    def multipoint(self, point_iterable):
        """A GeoTuple for MultiPoint representation."""
        return GeoTuple("MultiPoint", [self.point(p).coords for p in point_iterable])

    def with_node_nums(self, has_nodes, node_nums):
        """Does the work of looking up coordinate tuples for node number sequences"""
        p_lookup = has_nodes.nodes
        if len(node_nums) == 1:
            # single node
            return self.point(p_lookup[node_nums[0] - 1]).coords
        else:
            # node sequence
            return [self.point(p_lookup[p - 1]).coords for p in node_nums]

    def polygon(self, has_ijkl, has_nodes=None, *, strict=False):
        """A GeoTuple for Polygon representation.

        If strict is false, delegates to LineString if only 2 nodes.
        """
        if has_nodes is None:
            has_nodes = has_ijkl
        ijkl = [p for p in (getattr(has_ijkl, name) for name in "ijkl")]
        nums = [num for num in ijkl if num]
        result = self.with_node_nums(has_nodes, nums)
        if len(nums) == 2 and not strict and not self.strict:
            # will delegate to a LineString type in with_node_nums
            # LineStrings are not nested like Polygons
            return GeoTuple("LineString", result)
        elif len(nums) > 2:
            # Polygon needs to be nested in a list (first item is exterior ring, following items are holes)
            # assume no holes
            return GeoTuple("Polygon", [result])
        else:
            raise GeoInterfaceError("Invalid Polygon node numbering: (i={:d}, j={:d}, k={:d}, l={:d})".format(*ijkl))

    def node(self, has_node, has_nodes=None):
        """A GeoTuple for Point representation of has_node.node"""
        if has_nodes is None:
            has_nodes = has_node
        node_nums = [has_node.node]
        return GeoTuple("Point", self.with_node_nums(has_nodes, node_nums))

    def linestring(self, has_ij, has_nodes=None):
        """A GeoTuple for LineString representation."""
        if has_nodes is None:
            has_nodes = has_ij
        ij = [p for p in (getattr(has_ij, name) for name in "ij")]
        nums = [num for num in ij if num]
        if len(nums) != 2:
            raise GeoInterfaceError("Invalid LineString node numbering: (i={:d}, j={:d})".format(*ij))
        return GeoTuple("LineString", self.with_node_nums(has_nodes, nums))

    def multipolygon(self, polygon_iterable, *, strict=False):
        """A GeoTuple for MultiPolygon representation.

        If strict is false, attempts to delegate to MultiLineString.

        NOTE: ALL of the iterable items must be either 2 node only, OR a combination of 3 and 4 nodes
        """
        try:
            return GeoTuple("MultiPolygon", [self.polygon(p, polygon_iterable, strict=True).coords for p in polygon_iterable])
        except GeoInterfaceError as e1:
            if not strict and not self.strict:
                try:
                    return self.multilinestring(polygon_iterable)
                except GeoInterfaceError as e2:
                    raise e2 from e1
            raise e1

    def multinode(self, node_iterable):
        """A GeoTuple for MultiPoint representation of has_node.node for a sequence of has_nodes"""
        return GeoTuple("MultiPoint", [self.node(p, node_iterable).coords for p in node_iterable])

    def multilinestring(self, linestring_iterable):
        """A GeoTuple for MultiLineString representation."""
        return GeoTuple("MultiLineString", [self.linestring(p, linestring_iterable).coords for p in linestring_iterable])

    _lookup = dict(zip("Point Polygon LineString Node MultiPoint MultiPolygon MultiLineString MultiNode".split(),
                       (point, polygon, linestring, node, multipoint, multipolygon, multilinestring, multinode)))


class GeoMixin:
    """Adds  __geo_interface__ property

    The geo_type argument specifies the type of geometry. Choices are:
        - Point, MultiPoint, Polygon, LineString, MultiPolygon, MultiLineString
        - Any Polygon with only 2 valid points will delegate to a LineString instead
    """
    __geo_interface__: ClassVar[GeoInterface]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        try:
            geo_type = kwargs.pop("geo_type")
        except KeyError:
            raise GeoInterfaceError(f"geo_type argument required to subclass {cls.__qualname__}")
        cls.__geo_interface__ = GeoInterface(geo_type)
        super().__init_subclass__(**kwargs)


class WithKwargsMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        for k, v in kwargs.items():
            setattr(self, k, v)
