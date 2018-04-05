# -*- coding: utf-8 -*-

"""Contains the procedure for writing a `CidObj` to a .cid file."""
from itertools import chain, tee, repeat
from pathlib import Path
from typing import Iterator, TypeVar, Mapping, Type, Optional, Tuple

from .exc import CIDRWError
from ..utilities.dataclasses import unmapify, mapify, field_names
from ..cid import A1, A2, C1, C2, C3, C4, C5, D1, E1, Stop
from ..cid import CidLine

SEQ_TYPES = {A2: "pipe_groups", C3: "nodes", C4: "elements", C5: "boundaries", D1: "materials", E1: "factors"}
NON_SEQ_SUB_TYPES = {A1, C1, C2} | SEQ_TYPES.keys()

CidObj = TypeVar("CidObj")
CidLineType = Type[CidLine]

def process_lines(cid: CidObj, i_line_types: Iterator[CidLineType]) -> Iterator[CidLine]:
    while True:  # top level objects
        line_type = next(i_line_types)
        valid_fields = field_names(line_type)
        target_obj_name: Optional[str] = SEQ_TYPES.get(line_type, "")
        target_obj = getattr(cid, target_obj_name, cid)
        if target_obj is cid:
            target_obj = [target_obj]
        for subobj in target_obj:
            d: Mapping = mapify(subobj)
            yield unmapify(d, line_type, lambda k: k in valid_fields)
            while True:  # sub level objects
                # look ahead in `i_line_types`
                try:
                    prev_line_type, line_type = line_type, next(i_line_types)
                except StopIteration:
                    if line_type is Stop:
                        break
                    else:
                        raise CIDRWError("Encountered StopIteration before Stop object")
                if line_type in NON_SEQ_SUB_TYPES:
                    # put the iterated item back at the front and unswap line_type
                    i_line_types = chain([line_type], i_line_types)
                    line_type = prev_line_type
                    break
                else:
                    # line_type is a sub-type; use current subobj to write line
                    valid_fields = field_names(line_type)
                    yield unmapify(d, line_type, lambda k: k in valid_fields)

def lines_w_formatting(cid: CidObj, i_line_types: Iterator[CidLineType]) -> Iterator[Tuple[CidLine, str]]:
    """The line object and appropriate format code as a tuple: (line_obj, format_str)

    The number of objects in A1, C2 are updated to match lengths of sub-object sequences.
    """
    i_line_types1, i_line_types2 = tee(i_line_types)
    i_lines, i_line_types = zip(process_lines(cid, i_line_types1), i_line_types2)
    # TODO: write logic for this generator
    yield from zip(i_lines, repeat("cid"))

def line_strings(cid: CidObj, i_line_types: Iterator[CidLineType]) -> Iterator[str]:
    ilines_w_formatting = lines_w_formatting(cid, i_line_types)
    yield from (format(o, f) for o,f in ilines_w_formatting)

def file(cid: CidObj, i_line_types, path: Path, mode="x"):
    with path.open(mode):
        path.write_text("\n".join(line_strings(cid, i_line_types)))
