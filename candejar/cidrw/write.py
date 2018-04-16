# -*- coding: utf-8 -*-

"""Contains the procedure for writing an object to a .cid file."""

from itertools import chain, repeat
from pathlib import Path
from typing import Iterator, Mapping, Optional, Iterable, Collection, Union, Counter, Callable

from ..cidobjrw.names import SEQ_LINE_TYPE_NAME_DICT, SEQ_LINE_TYPE_TOTAL_DICT
from ..cid import TOP_LEVEL_TYPES, CIDL_FORMAT_TYPES
from ..utilities.cidobj import forgiving_dynamic_attr, SpecialError
from ..utilities.dataclasses import unmapify, shallow_mapify
from ..cid import Stop
from ..cid import CidLine
from .exc import CIDRWError
from . import CidObj, CidLineType, CidLineStr, FormatStr

def forgiving_cid_attr(cid: CidObj, attr_getter: Callable[[], Optional[str]]
                       ) -> Union[CidObj, Collection, str, int, float]:
    """Extends `forgiving_dynamic_attr` by raising `CIDRWError` when the
    requested cid attribute name is missing.
    """
    try:
        return forgiving_dynamic_attr(cid, attr_getter)
    except SpecialError:
        target_obj_name: Optional[str] = attr_getter()
        raise CIDRWError(f"Incomplete cid object: {target_obj_name!s} is missing")

def process_lines(cid: CidObj, line_types: Iterable[CidLineType]) -> Iterator[CidLine]:
    """Logic for producing `CidLine` instances from a cid object namespace and line type iterable."""
    line_type: Optional[CidLineType] = type(None)  # for testing after except statement
    i_line_types = iter(line_types)
    while True:  # top level objects loop
        try:
            line_type = next(i_line_types)
            target_obj = forgiving_cid_attr(cid, lambda: SEQ_LINE_TYPE_NAME_DICT.get(line_type))
            if target_obj is cid:
                target_obj = [target_obj]
            if not len(target_obj):
                raise CIDRWError(f"A {line_type.__name__} line type was encountered for processing but the "
                                 f"cid.{SEQ_LINE_TYPE_NAME_DICT[line_type]} collection is empty.")
            for subobj in target_obj:  # re-use same subobj for every line until new top-level line encountered
                # `valid_fields` and `line_type` already been iterated at this point
                # (either in top-level loop or sub level loop)
                d: Mapping = shallow_mapify(subobj)
                yield unmapify(d, line_type, lambda k: k in line_type.cidfields)  # A1, A2, C1, C2, D1, E1 yielded here
                while True:  # sub level objects loop
                    # look ahead in `i_line_types`
                    prev_line_type, line_type = line_type, next(i_line_types)
                    if line_type in TOP_LEVEL_TYPES:
                        # encountered an A2, C1, C3, C4, C5, D1, E1, or Stop - the B1 etc. or D2 etc. sub lines are complete;
                        # exit sub level objects loop
                        break
                    else:
                        # line_type is a sub-type; use current subobj to write line
                        yield unmapify(d, line_type, lambda k: k in line_type.cidfields)  # B1 etc., D2 etc. yielded here
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

def process_formatting(cid: CidObj, i_lines: Iterable[CidLine],
                       total_getter = lambda cid,t: forgiving_cid_attr(cid, lambda: SEQ_LINE_TYPE_TOTAL_DICT.get(t))
                       ) -> Iterator[FormatStr]:
    """The line object and appropriate format code as a tuple: (line_obj, format_str)

    The number of objects in A1, C2 (steps, nodes, elements, boundaries, soils materials, and interface materials)
    are updated to match lengths of sub-object sequences.
    The `A2.num` attribute (i.e., the number of pipe elements) for each pipe group is updated.

    By default the total_getter determines the correct total of each line_type (t) by a function that looks up the total
    defined by the cid object. Alternatively a different function could be provided such as one that counts the number
    of lines of that type in the subsequences of the cid object. Example:

        process_formatting(cid, i_lines, total_getter = lambda cid,t: len(getattr(cid, SEQ_LINE_TYPE_NAME_DICT[t])))
    """
    lines = list(i_lines)
    types = [type(x) for x in lines]
    type_totals = {t:total_getter(cid,t) for t in types}
    type_counter = Counter()
    format_strs = list(repeat("cid", len(lines)))
    for idx,t in enumerate(types):
        if t in CIDL_FORMAT_TYPES:
            type_counter[t] += 1
            if type_counter[t]>=type_totals[t]:
                format_strs[idx] += "L"
    yield from format_strs

def line_strings(cid: CidObj, line_types: Iterable[CidLineType]) -> Iterator[CidLineStr]:
    lines = list(process_lines(cid, line_types))
    i_formatting = process_formatting(cid, lines)
    yield from (format(o, f) for o,f in zip(lines,i_formatting))

def file(cid: CidObj, line_types: Iterable[CidLineType], path: Union[str, Path], mode: str="x") -> None:
    i_line_types = iter(line_types)
    with Path(path).open(mode):
        path.write_text("\n".join(line_strings(cid, i_line_types)))
