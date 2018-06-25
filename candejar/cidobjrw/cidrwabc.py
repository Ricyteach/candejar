# -*- coding: utf-8 -*-

"""Interface that provides reading/writing capability for .cid type objects."""

from __future__ import annotations
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Union, Iterator, Type, Iterable, Optional, TypeVar

from ..cid import CidLine
from ..cidprocessing.main import process
from ..cidrw.write import line_strings as write_line_strings, CidLineStr
from .exc import CidRWSubclassSignatureError


CidRWChild = TypeVar("CidRWChild", bound="CidRW")


class CidRW(ABC):
    """Abstract base class for read/write processing of .cid file types"""

    def __init_subclass__(cls: Type[CidRWChild], **kwargs) -> None:
        try:
            cls()
        except TypeError:
            raise CidRWSubclassSignatureError("Subclasses of CidRW must have "
                                              "default values provided for "
                                              "all arguments.")

    @classmethod
    def open(cls: Type[CidRWChild], path: Union[str, Path]) -> CidRWChild:
        """Make an instance from a .cid file."""
        path = Path(path).with_suffix(".cid")
        lines = path.read_text().split("\n")
        obj = cls()
        return obj.from_lines(lines)

    @classmethod
    @abstractmethod
    def from_lines(cls: Type[CidRWChild], lines: Optional[Iterable[CidLineStr]]=None,
                   line_types: Optional[Iterable[Type[CidLine]]]=None) -> CidRWChild:
        """Construct or edit an object instance from line string and line type inputs."""
        pass

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
        i_line_strings = write_line_strings(self, i_line_types)
        yield from i_line_strings

    def save(self, path: Union[str, Path], mode="x"):
        """Save .cid file to the path."""
        path = Path(path).with_suffix(".cid")
        with path.open(mode):
            path.write_text("\n".join(self.iter_line_strings()))
