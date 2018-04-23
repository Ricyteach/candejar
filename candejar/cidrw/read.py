# -*- coding: utf-8 -*-

"""Contains the procedure for reading a .cid file to an object."""

from typing import Iterable, Generator, Tuple, Type, Counter

from ..cidprocessing.exc import CIDProcessingIndexError
from ..cid.exc import LineParseError
from ..cid import CidLine, SEQ_LINE_TYPES
from ..cid import Stop
from .exc import IncompleteCIDLinesError, CIDLineProcessingError
from . import CidObj, CidLineType, CidLineStr

def line_strings(cid: CidObj, lines: Iterable[CidLineStr], line_types: Iterable[CidLineType],
                 handle_line_strs_in: Generator[None, Tuple[int, Type[CidLine]], None]) -> None:
    # start the generators and line iterator
    iter_lines = iter(lines)
    iter_line_types = iter(line_types)
    next(handle_line_strs_in)

    line_type = None
    for line_num,line in enumerate(iter_lines):
        try:
            line_type = next(iter_line_types)
        except StopIteration:
            if issubclass(line_type, Stop):
                break
            else:
                raise CIDLineProcessingError("An error occurred before "
                                             "processing was completed")
        else:
            handle_line_strs_in.send((line_num, line_type))
    # check for errors
    else:
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

    # check for leftover non-empty lines
    for line in iter_lines:
        if line.strip():
            raise CIDLineProcessingError("There appear to be extraneous "
                                         "data lines at the end of the file.")
    return cid
