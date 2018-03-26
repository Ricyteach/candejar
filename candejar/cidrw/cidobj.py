# -*- coding: utf-8 -*-

"""CID object module for working with an entire cid file as a read/write object."""
from dataclasses import dataclass, field, InitVar
from types import SimpleNamespace
from typing import List, Any, Optional, NewType, Sequence, Type
from ..utilities.chainsequences import ChainSequences
from ..cid.cidlineclasses import A1, A2, C1, C2, C3, C4, C5, D1, E1
from ..cid.cidline import CidLine
from ..cidprocessing.main import process as process_cid


MaterialNum = NewType("MaterialNum", int)
StepNum = NewType("StepNum", int)
InterfLink = NewType("InterfLink", int)


@dataclass
class PipeGroup:
    # only input parameter is lines
    line_objs: List[CidLine] = field(default_factory=list, repr=False)  # cid file line objects

    # all other fields are for display/output
    type_: str = field(default=AttributeDelegator("type_", "a2"), init=False)  # ALUMINUM, BASIC, CONCRETE, PLASTIC,
                                                                                # STEEL, CONRIB, CONTUBE


@dataclass
class Node:
    x: float = 0.0
    y: float = 0.0


@dataclass
class Element:
    i: Node
    j: Node
    k: Optional[Node] = None
    l: Optional[Node] = None
    mat: MaterialNum = 1
    step: StepNum = 1
    interflink: InterfLink = 0
    death: StepNum = 0


@dataclass
class Boundary:
    node: Node
    xcode: int = 0
    xvalue: float = 0.0
    ycode: int = 0
    yvalue: float = 0.0
    angle: float = 0.0
    pressure1: float = 0.0
    pressure2: float = 0.0


@dataclass
class Material:
    # only input parameter is lines
    line_obj: List[CidLine] = field(default_factory=list, repr=False)  # cid file line objects

    # all other fields are for display/output
    model: int = field(default=AttributeDelegator("model", "d1"), init=False)  # 1: Isotropic, 2: Orthotropic,
                                                                               # 3: Duncan/Selig, 4: Overburden,
                                                                               # 5: Extended Hardin, 6: Interface,
                                                                               # 7: Composite Link, 8: Mohr/Coulomb


@dataclass
class Factor:
    start: StepNum
    last: StepNum
    factor: float = 1.0
    comment: str = ""


class NumberedCidSubObj(SimpleNamespace):
    def __init__(self, num_, **kwargs):
        kwargs.pop("num", None)
        self.num = num_
        super().__init__(**kwargs)


class CidCollection(Sequence):
    type_dict = {A2: PipeGroup, C3: Node, C4: Element, C5: Boundary, D1: Material, E1: Factor, None: Thing}

    def __init__(self, cid_obj: "CidObjIn", type_: Type[CidLine]):
        self.type_ = type_
        self.cid_obj = cid_obj

    @property
    def iter_sequence(self):
        yield from (obj for obj in self.cid_obj.line_objs if isinstance(obj, self.type_))

    def __getitem__(self, idx: int) -> Any:
        for i,item in enumerate(self.iter_sequence):
            if i == idx:
                return item

    def __len__(self) -> int:
        return len(list(self.iter_sequence))


class AttributeDelegator:
    """Delegates attribute access to another named object attribute."""
    def __init__(self, name: str, delegate_name: str) -> None:
        self.delegate_name = delegate_name
        self.name = name
    """
    def __set_name__(self, owner, name):
        self.name = name
    """
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
    # only input parameter is lines; not stored
    lines: InitVar[List[CidLine]] = field(default=None)  # cid file line objects

    # all other fields are for display/output
    mode: int = field(default=AttributeDelegator("mode", "a1"), init=False)  # ANALYS or DESIGN
    level: int = field(default=AttributeDelegator("level", "a1"), init=False)  # 1, 2, 3
    method: int = field(default=AttributeDelegator("method", "a1"), init=False)  # 0=WSD, 1=LRFD
    ngroups: int = field(default=AttributeDelegator("ngroups", "a1"), init=False)  # pipe groups
    heading: int = field(default=AttributeDelegator("heading", "a1"), init=False)
    iterations: int = field(default=AttributeDelegator("iterations", "a1"), init=False)
    title: int = field(default=AttributeDelegator("title", "c1"), init=False)
    check: int = field(default=AttributeDelegator("check", "c2"), init=False)
    nsteps: int = field(default=AttributeDelegator("nsteps", "c2"), init=False)  # load steps
    nnodes: int = field(default=AttributeDelegator("nnodes", "c2"), init=False)
    nelements: int = field(default=AttributeDelegator("nelements", "c2"), init=False)
    nboundaries: int = field(default=AttributeDelegator("nboundaries", "c2"), init=False)
    nsoilmaterials: int = field(default=AttributeDelegator("nsoilmaterials", "c2"), init=False)
    ninterfmaterials: int = field(default=AttributeDelegator("ninterfmaterials", "c2"), init=False)

    # sequences of other cid objects
    groups: CidCollection = field(default_factory=list, init=False)  # pipe groups
    nodes: CidCollection = field(default_factory=list, init=False)
    elements: CidCollection = field(default_factory=list, init=False)
    boundaries: CidCollection = field(default_factory=list, init=False)
    soilmaterials: CidCollection = field(default_factory=list, init=False)  # soil element materials
    interfmaterials: CidCollection = field(default_factory=list, init=False)  # interface element materials
    factors: CidCollection = field(default_factory=list, init=False)  # lrfd step factors

    def __post_init__(self, lines):
        # cid file line objects stored; other objects are views
        if lines is None:
            lines = []
        self.line_objs: List[CidLine] = []
        # build pipe groups sequence
        iter_line_types = self.process_line_objs()
        for line in lines:
            line_type = next(iter_line_types)
            self.line_objs.append(line_type.parse(line))
            if isinstance(line_type, A2):
                self.groups.append(PipeGroup(self))

    def process_line_objs(self):
        yield from process_cid(self)

    @property
    def a1(self) -> A1:
        return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, A1))

    @property
    def c1(self) -> C1:
        return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, C1))

    @property
    def c2(self) -> C2:
        return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, C2))

    @property
    def materials(self):
        """The combination of the `soilmaterials`  and `interfmaterials` sequences."""
        return ChainSequences(self.soilmaterials, self.interfmaterials)
