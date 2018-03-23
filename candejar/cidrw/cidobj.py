# -*- coding: utf-8 -*-

"""CID object module for working with an entire cid file as a read/write object."""
from dataclasses import dataclass, field
from typing import List, Any, ClassVar
from ..cid.cidlineclasses import E1
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
class PipeGroup:
    # only input parameter is lines
    line_objs: List[CidLine] = field(default_factory=list, repr=False)  # cid file line objects

    # all other fields are for display/output
    type_: str = field(default=AttributeDelegator("a2"), init=False)  # ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL,
                                                                      # CONRIB, CONTUBE


@dataclass
class Material:
    # only input parameter is lines
    line_obj: List[CidLine] = field(default_factory=list, repr=False)  # cid file line objects

    # all other fields are for display/output
    model: int = field(default=AttributeDelegator("d1"), init=False)  # 1: Isotropic, 2: Orthotropic, # 3: Duncan/Selig,
                                                                      # 4: Overburden, # 5: Extended Hardin,
                                                                      # 6: Interface, 7: Composite Link, 8: Mohr/Coulomb


@dataclass
class CidObjIn:
    # only input parameter is lines
    line_objs: List[CidLine] = field(default_factory=list, repr=False)  # cid file line objects

    # all other fields are for display/output
    mode: int = field(default=AttributeDelegator("a1"), init=False)  # ANALYS or DESIGN
    level: int = field(default=AttributeDelegator("a1"), init=False)  # 1, 2, 3
    method: int = field(default=AttributeDelegator("a1"), init=False)  # 0=WSD, 1=LRFD
    ngroups: int = field(default=AttributeDelegator("a1"), init=False)  # pipe groups
    nsteps: int = field(default=AttributeDelegator("c2"), init=False)  # load steps
    nnodes: int = field(default=AttributeDelegator("c2"), init=False)
    nelements: int = field(default=AttributeDelegator("c2"), init=False)
    nboundaries: int = field(default=AttributeDelegator("c2"), init=False)
    nsoilmaterials: int = field(default=AttributeDelegator("c2"), init=False)
    ninterfmaterials: int = field(default=AttributeDelegator("c2"), init=False)
    groups: List[PipeGroup] = field(default_factory=list, init=False)  # pipe groups
    """
    nodes: List[Any] = field(default_factory=list, init=False)
    elements: List[Any] = field(default_factory=list, init=False)
    boundaries: List[Any] = field(default_factory=list, init=False)
    """
    materials: List[Material] = field(default_factory=list, init=False)  # element materials
    factors: List[E1] = field(default_factory=list, init=False)  # lrfd step factors

    @property
    def soilmaterials(self):
        return NotImplemented

    @property
    def interfmaterials(self):
        return NotImplemented
