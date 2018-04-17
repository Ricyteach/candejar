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
                 iter_line_strings_in: Generator[None, Tuple[Type[CidLine], CidLineStr], None]) -> None:
    # start the generators and line iterator
    iter_lines = iter(lines)
    iter_line_types = iter(line_types)
    next(iter_line_strings_in)
    line_type_ctr = Counter()

    line_type = None
    for line in iter_lines:
        try:
            while True:
                line_type = next(iter_line_types)
                try:
                    if line_type.__name__=="A2":
                        breakpoint()
                    line_obj = line_type.parse(line)
                    break
                except LineParseError:
                    if line_type in SEQ_LINE_TYPES:
                    # a section of lines ended; send signal to type iterator to move on to next section
                        iter_line_types.throw(CIDProcessingIndexError(f"Failed to retrieve {line_type.__name__} "
                                                                      f"line #{line_type_ctr[line_type]+1:d}"))
                    else:
                        raise
                    continue
            line_type_ctr[line_type] += 1
            iter_line_strings_in.send(line_obj)
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
