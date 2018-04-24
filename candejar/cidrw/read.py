# -*- coding: utf-8 -*-

"""Contains the procedure for reading a .cid file to an object."""
from itertools import count
from typing import Iterable, Generator, Tuple, Type, Counter

from ..cid import CidLine, SEQ_LINE_TYPES
from ..cid import Stop
from .exc import IncompleteCIDLinesError, CIDLineProcessingError
from . import CidObj, CidLineType, CidLineStr

def line_strings(cid: CidObj, lines: Iterable[CidLineStr], line_types: Iterable[CidLineType],
                 handle_line_strs_in: Generator[None, Tuple[int, Type[CidLine]], None]) -> None:
    # start the generators
    iter_line_types = iter(line_types)
    iter_line_strs = iter(lines)
    # initialize the line string handler for receiving
    next(handle_line_strs_in)

    line_type = None
    for line_idx,_ in enumerate(iter_line_strs):
        try:
            line_type = next(iter_line_types)
        except StopIteration:
            if issubclass(line_type, Stop):
                break
            else:
                raise CIDLineProcessingError("An error occurred before processing was completed")
        else:
            handle_line_strs_in.send((line_idx, line_type))
    # check for errors
    else:
        # check for completed processing
        if not issubclass(line_type, Stop):
            raise CIDLineProcessingError("STOP statement was not reached before encountering end of file.")
        # check for STOP
        try:
            next(iter_line_types)
        except StopIteration:
            pass
        else:
            raise IncompleteCIDLinesError(f"The .cid file appears to be incomplete. "
                                          f"Last encountered line type: {line_type.__name__}")

    # check for leftover non-empty lines
    leftovers = [line.strip() for line in iter_line_strs]
    if any(leftovers):
        raise CIDLineProcessingError(f"There appear to be {len(leftovers)!s} extraneous data lines at the end of the file.")
    return cid
