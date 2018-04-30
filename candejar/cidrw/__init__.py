# -*- coding: utf-8 -*-

"""Sub package for reading/writing (parsing/formatting) .cid files as a single
object."""

from typing import TypeVar, Type, NewType

from ..cid import CidLine, CidLineType

CidObj = TypeVar("CidObj")
CidLineStr = NewType("CidLineStr", str)
FormatStr = NewType("FormatStr", str)
