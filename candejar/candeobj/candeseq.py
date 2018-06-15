# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

import functools
import types
from abc import ABC
from typing import Callable, Any, Optional, TypeVar, Type, overload, Iterable, Sequence, Mapping, Generic

from . import exc
from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView, HasConverterMixin, ConvertingList

T = TypeVar("T")


class CandeList(ConvertingList[T]):
    """Extends ConvertingList with a better repr and for specialized subclassing"""
    __slots__ = ()

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({super().__repr__()})"


class CandeMapSequence(HasConverterMixin[T], KeyedChainView[T]):
    """Extends KeyedChainView to utilize converting member objects for the sub sequences (such as CandeList subclasses)
    """
    __slots__ = ()

    def __init__(self, seq_map: Optional[Mapping[Any, CandeList[T]]] = None, **kwargs: Iterable[T]) -> None:
        super().__init__(seq_map, **kwargs)
        for new_v in self.seq_map.values():
            self._check_sequence(new_v)

    @overload
    def __setitem__(self, i: int, v: T) -> None:
        ...

    @overload
    def __setitem__(self, s: slice, v: Iterable[T]) -> None:
        ...

    @overload
    def __setitem__(self, k: Any, v: Sequence[T]) -> None:
        ...

    def __setitem__(self, x, v):
        if not isinstance(v, Sequence):
            v = CandeList(v)
        super().__setitem__(x, v)
        if not (isinstance(x, slice) or isinstance(x, int)):
            new_v = self[x]
            self._check_sequence(new_v)

    @classmethod
    def _check_sequence(cls, v):
        """Checks converter attribute sequence requirement"""
        if not hasattr(v, "converter"):
            raise exc.CandeAttributeError(f"'converter' attribute required for chained {cls.__qualname__} sub sequences")
        if cls.converter is not v.converter:
            # might need to rethink this later....? doing this now for not other reason than it seems easiest.
            raise exc.CandeTypeError(f"the {cls.__qualname__} and {type(v).__qualname__} converters must be the same")


# For typing purposes only
class CandeSequence(ABC, Generic[T]):
    converter: Callable[[Any], T]


CandeSequence.register(CandeList)
CandeSequence.register(CandeMapSequence)

# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
candesequence_item_converter_dict = dict(pipegroups=types.SimpleNamespace,
                                         nodes=types.SimpleNamespace,
                                         elements=types.SimpleNamespace,
                                         boundaries=types.SimpleNamespace,
                                         soilmaterials=types.SimpleNamespace,
                                         interfmaterials=types.SimpleNamespace,
                                         factors=types.SimpleNamespace,
                                         )


def mapify_and_unpack_decorator(f: Callable[..., Any]) -> Callable[[Any], Any]:
    @functools.wraps(f)
    def wrapped(v: Any) -> Any:
        return f(**shallow_mapify(v))
    return wrapped


# noinspection PyPep8Naming
def make_cande_sequence_class(name: str, value_type: Optional[T] = None) -> Type[CandeSequence]:
    # get the item converter from the dictionary
    converter = candesequence_item_converter_dict[name.lower()]
    # the value_type is just for type annotation
    if value_type is None:
        if isinstance(converter, type):
            value_type = converter
        else:
            raise TypeError("CandeSequence container type needs to be specified for type checker when using a non-type "
                            "as a converter")
    # change the converter so it accepts a single argument instead of an unpacked map
    wrapped_converter = mapify_and_unpack_decorator(converter)
    if name in "Nodes Elements Boundaries".split():
        CandeSequenceType = CandeMapSequence
    elif name in "PipeGroups SoilMaterials InterfMaterials Factors".split():
        CandeSequenceType = CandeList
    else:
        raise ValueError(f"invalid cande object sequence attribute name: {name!s}")
    cls: Type[CandeSequence] = types.new_class(name, (CandeSequenceType[value_type],),
                                               dict(kwarg_convert=wrapped_converter))
    return cls


PipeGroups = make_cande_sequence_class("PipeGroups")
Nodes = make_cande_sequence_class("Nodes")
Elements = make_cande_sequence_class("Elements")
Boundaries = make_cande_sequence_class("Boundaries")
SoilMaterials = make_cande_sequence_class("SoilMaterials")
InterfMaterials = make_cande_sequence_class("InterfMaterials")
Factors = make_cande_sequence_class("Factors")

cande_seq_dict = dict(pipegroups=PipeGroups,
                      nodes=Nodes,
                      elements=Elements,
                      boundaries=Boundaries,
                      soilmaterials=SoilMaterials,
                      interfmaterials=InterfMaterials,
                      factors=Factors,
                      )


class NodesSection(CandeList[candesequence_item_converter_dict["nodes"]], kwarg_convert=Nodes.converter):
    pass


class ElementsSection(CandeList[candesequence_item_converter_dict["elements"]], kwarg_convert=Elements.converter):
    pass


class BoundariesSection(CandeList[candesequence_item_converter_dict["boundaries"]], kwarg_convert=Boundaries.converter):
    pass


cande_section_dict = dict(nodes=NodesSection,
                          elements=ElementsSection,
                          boundaries=BoundariesSection,
                          )
