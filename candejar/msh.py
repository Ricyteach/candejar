# -*- coding: utf-8 -*-

"""For creating msh geometry objects."""

from __future__ import annotations
from pathlib import Path
from typing import Union, Optional, Iterable, List
from dataclasses import dataclass, field

from .mshrw.read import line_strings as read_line_strings


def open(path: Union[str, Path]):
    path = Path(path)
    try:
        open_path = {".msh": Msh.open}[path.suffix.lower()]
    except KeyError:
        raise TypeError(f"{path.suffix!r} file not yet supported") from None
    return open_path(path)


@dataclass(repr=False)
class Msh:
    nodes: List = field(default_factory=list)
    elements: List = field(default_factory=list)
    boundaries: List = field(default_factory=list)

    @classmethod
    def open(cls, path: Union[str, Path]) -> Msh:
        """Make an instance from a .msh file."""
        path = Path(path).with_suffix(".msh")
        lines = path.read_text().split("\n")
        obj = cls()
        return obj.from_lines(lines)

    @classmethod
    def from_lines(cls, lines: Optional[Iterable[str]] = None) -> Msh:
        """Build an instance using line input strings

        If no lines or existing instance are provided, result is same as cls()
        """
        # initialize instance (should never require arguments)
        obj = cls()
        obj = read_line_strings(obj, lines)
        return obj

    def __repr__(self):
        return f"Msh({len(self.nodes)} nodes, {len(self.elements)} elements, {len(self.boundaries)} boundaries)"
