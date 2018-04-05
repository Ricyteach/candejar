# -*- coding: utf-8 -*-

"""Contains the procedure for writing a `CidObj` to a .cid file."""
from itertools import chain, tee, repeat
from pathlib import Path
from typing import Iterator, TypeVar, Mapping, Type, Optional, Tuple, Iterable, Collection, Union

from .exc import CIDRWError
from ..utilities.dataclasses import unmapify, mapify
from ..cid import A1, A2, C1, C2, C3, C4, C5, D1, E1, Stop
from ..cid import CidLine

SEQ_TYPES = {A2: "pipe_groups", C3: "nodes", C4: "elements", C5: "boundaries", D1: "materials", E1: "factors"}
SUB_SEQ_TERMINATORS = SEQ_TYPES.keys() | {C1, Stop}  # marks end of B1 etc. or D2 etc. sub lines

CidObj = TypeVar("CidObj")
CidLineType = Type[CidLine]

def get_target(cid: CidObj, line_type: CidLineType) -> Union[Collection, CidObj]:
    try:
        target_obj_name: str = SEQ_TYPES[line_type]
    except KeyError:
        return cid
    else:
        try:
            return getattr(cid, target_obj_name)
        except AttributeError:
            raise CIDRWError(f"Incomplete CidObj: {target_obj_name!s} collection is missing")

def process_lines(cid: CidObj, line_types: Iterable[CidLineType]) -> Iterator[CidLine]:
    """Logic for producing `CidLine` instances from a cid object namespace and line type iterable."""
    line_type: Optional[CidLineType] = type(None)  # for testing after except statement
    i_line_types = iter(line_types)
    while True:  # top level objects loop
        try:
            line_type = next(i_line_types)
            target_obj = get_target(cid, line_type)
            if target_obj is cid:
                target_obj = [target_obj]
            for subobj in target_obj:  # re-use same subobj for every line until new top-level line encountered
                # `valid_fields` and `line_type` already been iterated at this point
                # (either in top-level loop or sub level loop)
                d: Mapping = mapify(subobj)
                yield unmapify(d, line_type, lambda k: k in line_type.cidfields)
                while True:  # sub level objects loop
                    # look ahead in `i_line_types`
                    prev_line_type, line_type = line_type, next(i_line_types)
                    if line_type in SUB_SEQ_TERMINATORS:
                        # encountered an A2, C1, C3, C4, C5, D1, E1, or Stop - the B1 etc. or D2 etc. sub lines are complete;
                        # exit sub level objects loop
                        break
                    else:
                        # line_type is a sub-type; use current subobj to write line
                        yield unmapify(d, line_type, lambda k: k in line_type.cidfields)
            else:
                # cid subobj group (A2, C3, C4, C5, D1, or E1) complete; put the already iterated item back at the front
                i_line_types = chain([line_type], i_line_types)
        except StopIteration:
            if line_type is Stop:
                # end of cid line type processing successfully reached
                break
            else:
                raise CIDRWError(f"Encountered StopIteration before Stop object; last line type was "
                                 f"{line_type.__name__!s}")

def lines_w_formatting(cid: CidObj, line_types: Iterable[CidLineType]) -> Iterator[Tuple[CidLine, str]]:
    """The line object and appropriate format code as a tuple: (line_obj, format_str)

    The number of objects in A1, C2 (steps, nodes, elements, boundaries, soils materials, and interface materials)
    are updated to match lengths of sub-object sequences.
    The `A2.num` attribute (i.e., the number of pipe elements) for each pipe group is updated.
    """
    i_line_types = iter(line_types)
    i_lines = process_lines(cid, i_line_types)
    # TODO: write logic to match docstring for this generator
    yield from zip(i_lines, repeat("cid"))

def line_strings(cid: CidObj, line_types: Iterable[CidLineType]) -> Iterator[str]:
    i_line_types = iter(line_types)
    ilines_w_formatting = lines_w_formatting(cid, i_line_types)
    yield from (format(o, f) for o,f in ilines_w_formatting)

def file(cid: CidObj, line_types: Iterable[CidLineType], path: Path, mode: str="x") -> None:
    i_line_types = iter(line_types)
    with path.open(mode):
        path.write_text("\n".join(line_strings(cid, i_line_types)))
