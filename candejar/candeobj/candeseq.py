# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""
import types
from typing import Callable, Any, Iterable, Sequence, Mapping, Optional, TypeVar, Union

from .pipe_groups import PipeGroup, make_pipe_group
from ..utilities.collections import KeyedChainView

T = TypeVar("T")
V = TypeVar("V", bound = Mapping)
TorV = Union[T, V]

class CandeSequence(KeyedChainView[T]):
    __slots__ = ()

    def __init_subclass__(cls, *, kwarg_convert: Callable[..., T], **kwargs: Any) -> None:
        cls.converter = kwarg_convert
        super().__init_subclass__(**kwargs)

    def __init__(self, seq_map: Optional[Mapping[Any, Sequence[TorV]]] = None, **kwargs: Iterable[TorV]) -> None:
        if type(self) is CandeSequence:
            raise TypeError(f"cannot instantiate CandeSequence")
        super().__init__(seq_map, **kwargs)
        if isinstance(self.converter, type):
            coverter_is_cls = True
        else:
            coverter_is_cls = False
        for s in self.seq_map.values():
            for i,v in enumerate(s):
                if not coverter_is_cls or (coverter_is_cls and not isinstance(v, self.converter)):
                    s[i] = self.converter(**v)


# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
candesequence_converter_dict = dict(pipegroups = types.SimpleNamespace,
                                    nodes = types.SimpleNamespace,
                                    elements = types.SimpleNamespace,
                                    boundaries = types.SimpleNamespace,
                                    soilmaterials = types.SimpleNamespace,
                                    interfmaterials = types.SimpleNamespace,
                                    factors = types.SimpleNamespace,
                                    )


def make_candesequence(name):
    return types.new_class(name, (CandeSequence[PipeGroup], ), dict(kwarg_convert = candesequence_converter_dict[name.lower()]))


cande_seq_dict = dict(pipegroups = make_candesequence("PipeGroups"),
                      nodes = make_candesequence("Nodes"),
                      elements = make_candesequence("Elements"),
                      boundaries = make_candesequence("Boundaries"),
                      soilmaterials = make_candesequence("SoilMaterials"),
                      interfmaterials = make_candesequence("InterfMaterials"),
                      factors = make_candesequence("Factors"),
                      )
