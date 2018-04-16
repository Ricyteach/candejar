# -*- coding: utf-8 -*-

"""Contains the procedure for reading a .cid file to an object."""

from typing import Iterable, Generator, Tuple, Type

from ..cid import CidLine
from ..cid import Stop
from .exc import IncompleteCIDLinesError, CIDLineProcessingError
from . import CidObj, CidLineType, CidLineStr

def line_strings(cid: CidObj, lines: Iterable[CidLineStr],
                 iter_line_types: Iterable[CidLineType],
                 iter_line_strings_in: Generator[None, Tuple[Type[CidLine], CidLineStr], None]) -> None:
    # start the receiving generator and line iterator
    iter_lines = iter(lines)
    next(iter_line_strings_in)

    line_type = None
    for line in iter_lines:
        try:
            line_type = next(iter_line_types)
            iter_line_strings_in.send((line_type, line))
        except StopIteration:
            if issubclass(line_type, Stop):
                break
            else:
                raise CIDLineProcessingError("An error occurred before "
                                             "processing was completed")
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

    # check for leftover lines
    for line in iter_lines:
        if line.strip():
            raise CIDLineProcessingError("There appear to be extraneous "
                                         "data lines at the end of the file.")
    return cid
