# -*- coding: utf-8 -*-

"""CID object module for working with an entire cid file as a read/write object."""

from dataclasses import dataclass, field, InitVar
from typing import List, Any, Type, Iterator, Iterable, Optional

from .. import fea
from ..cid import CidLine, A1, A2, C1, C2, C3, C4, C5, D1, E1, Stop
from .exc import CIDRWError
from ..utilities.collections import ChainSequence
from ..cidprocessing.main import process as process_cid
from .cidseq import CidSeq, Materials
from .cidseq.names import SEQ_NAMES, SEQ_CLASS_NAMES

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
class CidObj:
    # only input parameter is lines; not stored
    lines: InitVar[Optional[Iterable[str]]] = field(default=None)  # cid file line objects

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

    # sub-sequences of other cid objects; must appear in SEQ_NAMES
    pipe_groups: CidSeq["CidObj", A2, fea.PipeGroup] = field(default_factory=list, init=False)  # pipe groups
    nodes: CidSeq["CidObj", C3, fea.Node] = field(default_factory=list, init=False)
    elements: CidSeq["CidObj", C4, fea.Element] = field(default_factory=list, init=False)
    boundaries: CidSeq["CidObj", C5, fea.Boundary] = field(default_factory=list, init=False)
    soilmaterials: CidSeq["CidObj", D1, fea.Material] = field(default_factory=list, init=False)  # soil element materials
    interfmaterials: CidSeq["CidObj", D1, fea.Material] = field(default_factory=list, init=False)  # interface element materials
    factors: CidSeq["CidObj", E1, fea.Factor] = field(default_factory=list, init=False)  # lrfd step factors

    def __post_init__(self, lines: Optional[Iterable[str]]) -> None:
        # initialize empty sub-sequences of other cid objects
        for seq_name, seq_cls_name in zip(SEQ_NAMES, SEQ_CLASS_NAMES):
            # skip materials sequence; consists of soil and interf material sub sequences
            if seq_name == "materials":
                continue
            existing_seq_obj = getattr(self, seq_name)
            seq_obj = CidSeq.subclasses[seq_cls_name](self)
            if isinstance(existing_seq_obj, CidSeq):
                seq_obj.set_seq(existing_seq_obj.seq)
            elif existing_seq_obj:
                seq_obj.set_seq(existing_seq_obj)
            if any(not issubclass(obj.fea_obj, seq_obj.type_) for obj in existing_seq_obj):
                i, c = next(enumerate(o for o in existing_seq_obj if not issubclass(o.fea_obj, seq_obj.type_)))
                raise CIDRWError(f"The class ({c.__name__}) of item seq[{i}] is not a {seq_obj.type_.__name__} subclass.")
            setattr(self, seq_name, seq_obj)

        # cid file line objects stored; other objects are views
        if lines is None:
            lines = []
        self.line_objs: List[CidLine] = []
        # build line_objs sequence
        iter_line_types = self.process_line_objs()
        for line in lines:
            try:
                line_type = next(iter_line_types)
            except StopIteration:
                if line.strip() and not isinstance(self.line_objs[-1], Stop):
                    raise CIDRWError("End of file reached before encountering"
                                     "STOP statement.")
            else:
                self.line_objs.append(line_type.parse(line))

    def process_line_objs(self) -> Iterator[Type[CidLine]]:
        yield from process_cid(self)

    @property
    def a1(self) -> A1:
        try:
            return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, A1))
        except StopIteration:
            return A1()

    @property
    def c1(self) -> C1:
        try:
            return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, C1))
        except StopIteration:
            return C1()

    @property
    def c2(self) -> C2:
        try:
            return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, C2))
        except StopIteration:
            return C2()

    @property
    def materials(self) -> CidSeq["CidObj", D1, fea.Material]:
        """The combination of the `soilmaterials`  and `interfmaterials` sequences."""
        seq_obj = Materials(self)
        seq_obj.set_seq(ChainSequence(self.soilmaterials, self.interfmaterials))
        return seq_obj
