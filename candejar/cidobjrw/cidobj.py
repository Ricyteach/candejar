# -*- coding: utf-8 -*-

"""CID object module for working with an entire cid file as a read/write Python
data model object."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Any, Iterable, Optional, Generator, Tuple, Type, Sequence

from ..utilities.descriptors import AttributeDelegator
from ..cidrw.write import CidLineStr
from ..cidrw.read import line_strings as read_line_strings
from ..cid import SEQ_LINE_TYPES, TOP_LEVEL_TYPES, CidLine, A1, A2, C1, C2, C3, C4, C5, D1, E1, Stop
from ..cid.exc import LineParseError
from .names import ALL_SEQ_NAMES, SEQ_NAMES_DICT
from .cidrwabc import CidRW
from .cidseq import CidSeq, COMPLETE
from .cidseq.names import ALL_SEQ_CLASS_NAMES
from .exc import CidObjFromLinesError

EXCLUDED_CHECK_COMPLETE_TYPES = (A1, A2, C1, C2, D1, Stop)


@dataclass
class CidObj(CidRW):
    """A data viewer for working with a .cid file as a Python data model object.

    Note that the `CidObj` does not necessarily define a `dataclass` field for
    every cid A1, C1, and C2 field. This means, for example, that an input cid
    file read into `CidObj` will change all non-included fields to *default values*
    when it is mapified and/or written, since mapify grabs only from `dataclass`
    fields (if they exist).

    A `list` of cid file line objects is stored in `line_objs`. Other members are
    on-the-fly views of the data contained in the line objects. However `line_objs`
    is not a `dataclass` field.
    """
    # fields are for display/output
    mode: str = field(default=AttributeDelegator("a1"))  # ANALYS or DESIGN
    level: int = field(default=AttributeDelegator("a1"))  # 1, 2, 3
    method: int = field(default=AttributeDelegator("a1"))  # 0=WSD, 1=LRFD
    ngroups: int = field(default=AttributeDelegator("a1"))  # pipe groups
    heading: str = field(default=AttributeDelegator("a1"))
    iterations: int = field(default=AttributeDelegator("a1"))
    title: str = field(default=AttributeDelegator("c1"))
    check: int = field(default=AttributeDelegator("c2"))
    nsteps: int = field(default=AttributeDelegator("c2"))  # load steps
    nnodes: int = field(default=AttributeDelegator("c2"))
    nelements: int = field(default=AttributeDelegator("c2"))
    nboundaries: int = field(default=AttributeDelegator("c2"))
    nsoilmaterials: int = field(default=AttributeDelegator("c2"))
    ninterfmaterials: int = field(default=AttributeDelegator("c2"))

    @property
    def nmaterials(self) -> int:
        return self.nsoilmaterials + self.ninterfmaterials

    # sub-sequences of other cid objects; must appear in ALL_SEQ_NAMES
    pipegroups: CidSeq[CidObj, A2] = field(default=None, repr=False)  # pipe groups
    nodes: CidSeq[CidObj, C3] = field(default=None, repr=False)
    elements: CidSeq[CidObj, C4] = field(default=None, repr=False)
    boundaries: CidSeq[CidObj, C5] = field(default=None, repr=False)
    materials: CidSeq[CidObj, D1] = field(default=None, repr=False)  # all element materials
    soilmaterials: CidSeq[CidObj, D1] = field(default=None, repr=False)  # soil element materials
    interfmaterials: CidSeq[CidObj, D1] = field(default=None, repr=False)  # interface element materials
    factors: CidSeq[CidObj, E1] = field(default=None, repr=False)  # lrfd step factors

    def __post_init__(self) -> None:
        # initialize empty cid sub object sequence types
        for seq_name, seq_cls_name in zip(ALL_SEQ_NAMES, ALL_SEQ_CLASS_NAMES):
            # initialize new empty sequence; specify `CidObj` as the Generic input type
            if getattr(self, seq_name) is None:
                seq_obj = CidSeq.getsubcls(seq_cls_name)[CidObj](self)
                setattr(self, seq_name, seq_obj)
        # initialize empty line_objs list
        self.line_objs: List[CidLine] = []

    @classmethod
    def from_lines(cls, lines: Optional[Sequence[CidLineStr]]=None,
                   line_types: Optional[Iterable[Type[CidLine]]]=None) -> CidRW:
        """Build an instance using line input strings and line types

        If no lines or existing instance are provided, result is same as cls()
        """
        # initialize instance (should never require arguments)
        obj = cls()
        if lines:
            handle_line_strs_in = obj.handle_line_strs(lines)
            iter_line_types = obj.process_line_types() if line_types is None else iter(line_types)
            read_line_strings(obj, lines, iter_line_types, handle_line_strs_in)
        else:
            if line_types is not None:
                raise CidObjFromLinesError(f"Cannot build a {cls.__name__} instance "
                                           f"using only line type input")
        return obj

    def handle_line_strs(self, lines: Sequence[CidLineStr]) -> Generator[None, Tuple[int, Type[CidLine]], None]:
        """Creates the line_objs list and adds the parsed line objects that constitute the object state.

        Utilizes next_seq.check_complete = None AND cidseq.COMPLETE to signal the start AND end of line type sequences.
        """
        # for tracking sub sequence sections
        curr_section_typ = None
        next_section_typ = A1

        # for setting check_complete
        next_seq = None

        # line string processing procedure
        while True:
            # receive information to produce next line object
            line_idx, line_type = yield
            curr_line_str = lines[line_idx]
            # create line object
            line_obj = line_type.parse(curr_line_str)
            # add to the line_objs collection
            self.line_objs.append(line_obj)
            # the STOP object signals the end of processing
            if issubclass(line_type, Stop):
                break

            # check if the top level section changed
            if line_type in TOP_LEVEL_TYPES and curr_section_typ != line_type:
                # note the previous section
                prev_section_typ = curr_section_typ
                # note the current section
                curr_section_typ = line_type
                # get the PREDICTED next section
                next_section_typ = self.next_section_type(line_type)
                # check if the next section is a sequence
                if next_section_typ in SEQ_LINE_TYPES:
                    # set next_seq.check_complete to None
                    try:
                        next_seq_name = SEQ_NAMES_DICT[next_section_typ]
                        next_seq = getattr(self, next_seq_name)
                    except KeyError as e:
                        raise CidObjFromLinesError(f"the name of the {type(self).__qualname__} object sequence attribute "
                                                   f"could not be determined from {next_section_typ.__qualname__}") from e
                    except AttributeError as e:
                        raise CidObjFromLinesError(f"{type(self).__name__} object is missing "
                                                   f"{next_seq_name} sub sequence") from e
                    next_seq.check_complete = None

            # only worry about signaling complete sequences for specific line types
            if line_type not in EXCLUDED_CHECK_COMPLETE_TYPES:
                # determine if COMPLETE signal should be sent for current sub sequence based on next line
                next_line_str = lines[line_idx+1]
                # see if a parse attempt on next line will succeed for next section
                try:
                    next_section_typ.parse(next_line_str)
                # if it fails, do nothing; probably will succeed with next parser sent
                except LineParseError:
                    pass
                # if it succeeds, current section is complete; send signal
                else:
                    try:
                        next_seq.check_complete = COMPLETE
                    except AttributeError:
                        CidObjFromLinesError("an invalid series of types was sent to the generator")

        # check that the generator was sent some top level line types
        if curr_section_typ is None:
            raise CidObjFromLinesError("No top level line types were sent") from None
        # pause after Stop, before completion (to prevent StopIteration)
        yield

    def next_section_type(self, line_type:Type[CidLine]) -> Type[CidLine]:
        """Calculate the next section line type that should be attempted for parsing the next cid section."""
        d={A1:A2, A2:C1, C1:C2, C2:C3, C3:C4, C4:C5, C5:D1, D1:(E1 if self.method==1 else Stop), E1:Stop}
        return d[line_type]

    @property
    def a1(self) -> A1:
        try:
            return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, A1))
        except (StopIteration, AttributeError):
            return A1()

    @property
    def c1(self) -> C1:
        try:
            return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, C1))
        except (StopIteration, AttributeError):
            return C1()

    @property
    def c2(self) -> C2:
        try:
            return next(line_obj for line_obj in self.line_objs if isinstance(line_obj, C2))
        except (StopIteration, AttributeError):
            return C2()
