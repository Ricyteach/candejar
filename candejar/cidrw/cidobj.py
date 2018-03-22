# -*- coding: utf-8 -*-

"""CID object module for working with an entire cid file as a read/write object."""
from dataclasses import dataclass, field
from typing import List, Any, ClassVar
from ..cid.cidline import CidLine


class AttributeDelegator:
    """Delegates attribute access to another named object attribute."""
    def __init__(self, delegate_name: str, transform = lambda s: s) -> None:
        self.delegate_name = transform(delegate_name)
    def __set_name__(self, owner: Any, name: str) -> None:
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

@dataclass
class CidObjIn:
    lines: List[CidLine] = field(default_factory=list, repr=False)  # cid file lines
    groups: List[Any] = field(default_factory=list, repr=False, init=False)  # pipe groups
    nodes: List[Any] = field(default_factory=list, repr=False, init=False)
    elements: List[Any] = field(default_factory=list, repr=False, init=False)
    boundaries: List[Any] = field(default_factory=list, repr=False, init=False)
    materials: List[Any] = field(default_factory=list, repr=False, init=False)  # element materials
    factors: List[Any] = field(default_factory=list, repr=False, init=False)  # lrfd step factors
    level: int = AttributeDelegator("a1")  # 1, 2, 3
    method: int = AttributeDelegator("a1")  # 0=WSD, 1=LRFD
    mode: int = AttributeDelegator("a1")  # ANALYS or DESIGN
    ngroups: int = AttributeDelegator("a1")  # pipe groups
    nsteps: int = AttributeDelegator("c2")  # load steps
    nnodes: int = AttributeDelegator("c2")
    nelements: int = AttributeDelegator("c2")
    nboundaries: int = AttributeDelegator("c2")
    nsoil_materials: int = AttributeDelegator("c2")
    ninterf_materials: int = AttributeDelegator("c2")

    @property
    def soilmaterials(self):
        return NotImplemented

    @property
    def interfmaterials(self):
        return NotImplemented
