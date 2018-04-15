# -*- coding: utf-8 -*-

"""CID object module for working with an entire cid file as a read/write Python data model object."""

from dataclasses import dataclass, field, InitVar
from typing import List, Any, Iterable, Optional, Generator, Tuple

from ..cidrw.write import CidLineStr
from .cidseq.names import ALL_SEQ_CLASS_NAMES
from .names import ALL_SEQ_NAMES
from .. import fea
from ..cid import CidLine, A1, A2, C1, C2, C3, C4, C5, D1, E1, Stop
from .exc import IncompleteCIDLinesError, CIDLineProcessingError
from .cidrwabc import CidRW
from .cidseq import CidSeq


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
class CidObj(CidRW):
    """A data viewer for working with a .cid file as a Python data model object.

    Note that the `CidObj` does not necessarily define a `dataclass` field for every cid A1, C1, and C2 field. This means,
    for example, that an input cid file read into `CidObj` will change all non-included fields to *default values* when it
    mapified and/or written, since mapify grabs only from `dataclass` fields (if they exist).

    A `list` of cid file line objects is stored in `line_objs`. Other members are on-the-fly views of the data contained
    in the line objects. However `line_objs` is not a `dataclass` field.
    """
    # only input parameter is lines; not stored (converted to cid line objects)
    lines: InitVar[Optional[Iterable[str]]] = field(default=None)  # cid file line objects

    # all other fields are for display/output
    mode: str = field(default=AttributeDelegator("mode", "a1"), init=False)  # ANALYS or DESIGN
    level: int = field(default=AttributeDelegator("level", "a1"), init=False)  # 1, 2, 3
    method: int = field(default=AttributeDelegator("method", "a1"), init=False)  # 0=WSD, 1=LRFD
    ngroups: int = field(default=AttributeDelegator("ngroups", "a1"), init=False)  # pipe groups
    heading: str = field(default=AttributeDelegator("heading", "a1"), init=False)
    iterations: int = field(default=AttributeDelegator("iterations", "a1"), init=False)
    title: str = field(default=AttributeDelegator("title", "c1"), init=False)
    check: int = field(default=AttributeDelegator("check", "c2"), init=False)
    nsteps: int = field(default=AttributeDelegator("nsteps", "c2"), init=False)  # load steps
    nnodes: int = field(default=AttributeDelegator("nnodes", "c2"), init=False)
    nelements: int = field(default=AttributeDelegator("nelements", "c2"), init=False)
    nboundaries: int = field(default=AttributeDelegator("nboundaries", "c2"), init=False)
    nsoilmaterials: int = field(default=AttributeDelegator("nsoilmaterials", "c2"), init=False)
    ninterfmaterials: int = field(default=AttributeDelegator("ninterfmaterials", "c2"), init=False)

    @property
    def nmaterials(self) -> int:
        return self.nsoilmaterials + self.ninterfmaterials

    # sub-sequences of other cid objects; must appear in ALL_SEQ_NAMES
    pipe_groups: CidSeq["CidObj", A2, fea.PipeGroup] = field(default=None, init=False, repr=False)  # pipe groups
    nodes: CidSeq["CidObj", C3, fea.Node] = field(default=None, init=False, repr=False)
    elements: CidSeq["CidObj", C4, fea.Element] = field(default=None, init=False, repr=False)
    boundaries: CidSeq["CidObj", C5, fea.Boundary] = field(default=None, init=False, repr=False)
    materials: CidSeq["CidObj", D1, fea.Material] = field(default=None, init=False, repr=False)  # all element materials
    soilmaterials: CidSeq["CidObj", D1, fea.Material] = field(default=None, init=False, repr=False)  # soil element materials
    interfmaterials: CidSeq["CidObj", D1, fea.Material] = field(default=None, init=False, repr=False)  # interface element materials
    factors: CidSeq["CidObj", E1, fea.Factor] = field(default=None, init=False, repr=False)  # lrfd step factors

    def __post_init__(self, lines: Optional[Iterable[str]]) -> None:
        # initialize empty cid sub object sequence types
        for seq_name, seq_cls_name in zip(ALL_SEQ_NAMES, ALL_SEQ_CLASS_NAMES):
            # initialize new empty sequence
            seq_obj = CidSeq.subclasses[seq_cls_name](self)
            setattr(self, seq_name, seq_obj)

        # initialize empty line_objs list
        self.line_objs: List[CidLine] = []

        if lines is None:
            # no lines provided
            return

        # build line_objs sequence
        iter_line_types = self.process_line_types()
        iter_lines = iter(lines)
        line_type = None
        for line in iter_lines:
            try:
                line_type = next(iter_line_types)
            except StopIteration:
                if issubclass(line_type, Stop):
                    break
                else:
                    raise CIDLineProcessingError("An error occurred before "
                                                 "processing was completed")
            else:
                self.line_objs.append(line_type.parse(line))
        # check for errors
        if lines:
            # check for completed processing
            if not issubclass(line_type, Stop):
                raise CIDLineProcessingError("STOP statement was not reached "
                                             "before encountering end of file.")
            # check for STOP
            try:
                next(iter_line_types)
            except StopIteration:
                pass
            else:
                raise IncompleteCIDLinesError(f"The .cid file appears to be incomplete. "
                                              f"Last encountered line type: {line_type.__name__}")

        # check for leftover lines
        for line in iter_lines:
            if line.strip():
                raise CIDLineProcessingError("There appear to be extraneous "
                                             "data lines at the end of the file.")

    def process_line_strings(self) -> Generator[None, Tuple[CidLine, CidLineStr], None]:
        """Creates the line_objs list and adds the parsed line objects that
        constitute the object state
        """
        # initialize empty line_objs list
        self.line_objs: List[CidLine] = []
        while True:
            # receive line string
            line_type, line = yield
            # create line object
            self.line_objs.append(line_type.parse(line))
            # the STOP object signals the end of processing
            if issubclass(line_type, Stop):
                break

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
