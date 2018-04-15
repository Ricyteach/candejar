# -*- coding: utf-8 -*-

"""Interface that provides reading/writing capability for .cid type objects."""

from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union, Iterator, Type, Iterable, Optional, Tuple, Generator

from ..cid import CidLine
from ..cidobjrw.exc import CidRWSubclassSignatureError
from ..cidprocessing.main import process
from ..cidrw.write import line_strings, CidLineStr, parse


class CidRW(ABC):
    """Mixin class for read/write processing of .cid file types"""

    def __init_subclass__(cls, **kwargs):
        try:
            cls()
        except TypeError:
            raise CidRWSubclassSignatureError("Subclasses of CidRW must have "
                                              "default values provided for "
                                              "all arguments.")

    @abstractmethod
    def process_line_strings(self) -> Generator[None, Tuple[Type[CidLine], CidLineStr], None]:
        """Handle line inputs in the process of constructing an object instance."""
        pass

    @classmethod
    def open(cls, path: Union[str, Path]) -> "CidRW":
        """Make an instance from a .cid file."""
        path = Path(path).with_suffix(".cid")
        lines = path.read_text().split("\n")
        return cls.from_lines(lines)

    @classmethod
    def from_lines(cls, lines: Optional[Iterable[CidLineStr]]=None) -> "CidRW":
        """Build an instance using line input strings"""
        # initialize instance (should never require arguments)
        obj = cls()
        obj._post_init(lines)
        return  obj

    def _post_init(self, lines: Optional[Iterable[CidLineStr]]=None) -> None:
        # if no lines provided, result is same as cls()
        if lines is not None:
            iter_line_types = self.process_line_types()
            iter_line_strings_in = self.process_line_strings()
            parse(self, lines, iter_line_types, iter_line_strings_in)

    def process_line_types(self) -> Iterator[Type[CidLine]]:
        """A line object type iterator that determines the next line object
        type based on the current state of the object, which represents the
        CANDE file and/or problem."""
        yield from process(self)

    def iter_line_strings(self) -> Iterator[CidLineStr]:
        """The formatted .cid file line strings from current object state.

        The number of objects in A1, C2 are updated to match lengths of sub-object sequences.
        """
        i_line_types = self.process_line_types()
        i_line_strings = line_strings(self, i_line_types)
        yield from i_line_strings

    def save(self, path: Union[str, Path], mode="x"):
        """Save .cid file to the path."""
        path = Path(path).with_suffix(".cid")
        with path.open(mode):
            path.write_text("\n".join(self.iter_line_strings()))
