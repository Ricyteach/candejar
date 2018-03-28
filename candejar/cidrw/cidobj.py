# -*- coding: utf-8 -*-

"""CID object module for working with an entire cid file as a read/write object."""

from dataclasses import dataclass, field, InitVar, fields, asdict
from typing import List, Any, Sequence, Type, TypeVar, MutableSequence, Generic, Union, Iterable

from .exc import CIDRWError
from ..utilities.collections import MyCounter, ChainSequence
from ..cid.cidlineclasses import A1, A2, C1, C2, C3, C4, C5, D1, E1, Stop
from ..cid.cidline import CidLine
from ..cidprocessing.main import process as process_cid
from ..fea.objs import PipeGroup, Node, Element, Boundary, Material, Factor

class CIDSubSeqError(CIDRWError):
    pass

FEAObj = TypeVar("FEAObj", PipeGroup, Node, Element, Boundary, Material, Factor)
CidSubLine = TypeVar("CidSubLine", A2, C3, C4, C5, D1, E1)

TYPE_DICT = {A2: PipeGroup, C3: Node, C4: Element, C5: Boundary, D1: Material, E1: Factor}
SEQ_NAME_DICT = {"pipe_groups": A2, "nodes": C3, "elements": C4, "boundaries": C5, "soilmaterials": D1, "interfmaterials": D1, "factors": E1}


class CidSubObj(Generic[CidSubLine, FEAObj]):

    def __init__(self, container: "CidSubSeq", idx: int) -> None:
        self.container = container
        self.idx = idx

    @property
    def cid_obj(self) -> "CidObj":
        return self.container.cid_obj

    @property
    def line_type(self) -> Type[CidSubLine]:
        return self.container.line_type

    @property
    def iter_line_objs(self) -> Iterable[CidLine]:
        i_line_objs = iter(self.cid_obj.line_objs)
        num = self.idx + 1
        start_ctr = MyCounter()
        for line in i_line_objs:
            start_ctr[isinstance(line, self.line_type)] += 1
            if start_ctr[True] == num:
                yield line
                break
        else:
            raise CIDRWError(f"Could not locate {self.line_type.__name__!s} object number {num!s}")
        for line in i_line_objs:
            if not isinstance(line, self.line_type):
                yield line
            else:
                break

    @property
    def fea_obj(self) -> FEAObj:
        field_names = [f.name for f in fields(self.container.type_)]
        #  NOTE: major bug below, currently: most fields/attributes for Material and PipeGroup objects are being lost
        #  Need to think of a way to fix
        return self.container.type_(**{k:v for line_obj in self.iter_line_objs for k,v in asdict(line_obj).items() if k in field_names})

    def __getattr__(self, attr: str) -> Union[int, float, str]:
        for line_obj in self.iter_line_objs:
            try:
                return getattr(line_obj, attr)
            except AttributeError:
                continue
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {attr!r}")


class CidSubSeq(Sequence[CidSubObj], Generic[CidSubLine, FEAObj]):

    def __init__(self, cid_obj: "CidObj", seq_name: str) -> None:
        self.cid_obj = cid_obj
        self.line_type = SEQ_NAME_DICT[seq_name]
        if getattr(self.cid_obj, seq_name):
            self.seq = getattr(self.cid_obj, seq_name)
            if any(not issubclass(obj.type_, self.type_) for obj in self.seq):
                i, c = next(enumerate(o for o in self.seq if not issubclass(o, self.type_)))
                raise CIDRWError(f"The class ({c.__name__}) of item seq[{i}] is not a {self.type_.__name__} subclass.")
        else:
            self.seq: Sequence[CidSubObj] = []

    @property
    def type_(self) -> Type[FEAObj]:
        return TYPE_DICT[self.line_type]

    @property
    def iter_sequence(self):
        yield from (obj for obj in self.cid_obj.line_objs if isinstance(obj, self.line_type))

    def update_seq(self) -> None:
        i_seq =self.iter_sequence
        for i,_ in enumerate(self.seq):
            try:
                next(i_seq)
            except StopIteration:
                raise CIDSubSeqError(f"The CidSubSeq object [{i}] has no corresponding line object.")
        for _ in i_seq:
            obj = CidSubObj(self, len(self))
            self.seq.append(obj)

    def __getitem__(self, idx: int) -> CidSubObj:
        try:
            self.update_seq()
        except CIDSubSeqError:
            raise IndexError(f"Index [{idx:d}] exceeds available indexes for {self.line_type.__name__} objects")
        return self.seq[idx]

    def __len__(self) -> int:
        try:
            s = self.seq
        except AttributeError:
            return 0
        else:
            return len(s)


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

    # sub-sequences of other cid objects; must appear in SEQ_NAME_DICT
    pipe_groups: Sequence[CidSubObj] = field(default_factory=list, init=False)  # pipe groups
    nodes: Sequence[CidSubObj] = field(default_factory=list, init=False)
    elements: Sequence[CidSubObj] = field(default_factory=list, init=False)
    boundaries: Sequence[CidSubObj] = field(default_factory=list, init=False)
    soilmaterials: Sequence[CidSubObj] = field(default_factory=list, init=False)  # soil element materials
    interfmaterials: Sequence[CidSubObj] = field(default_factory=list, init=False)  # interface element materials
    factors: Sequence[CidSubObj] = field(default_factory=list, init=False)  # lrfd step factors

    def __post_init__(self, lines):
        # initialize empty sub-sequences of other cid objects
        for seq_name in SEQ_NAME_DICT:
            if not getattr(self, seq_name):
                setattr(self, seq_name, CidSubSeq(self, seq_name))

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
                if line and not isinstance(self.line_objs[-1], Stop):
                    raise CIDRWError("End of file reached before encountering"
                                     "STOP statement.")
            else:
                self.line_objs.append(line_type.parse(line))
            """
            if isinstance(line_type, A2):
                self.pipe_groups.append(PipeGroup(self))
            """

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
        return ChainSequence(self.soilmaterials, self.interfmaterials)
