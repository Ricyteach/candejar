# -*- coding: utf-8 -*-

"""Sub package for reading/writing (parsing/formatting) lines of .cid files."""
from typing import TypeVar

from .cidlineclasses import *
from .cidline import CidLine

CidSubLine = TypeVar("CidSubLine", A2, C3, C4, C5, D1, E1)
