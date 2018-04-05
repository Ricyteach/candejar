# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Collection


class CidABC(metaclass=ABCMeta):
    def __new__(cls, *args, **kwargs):
        if cls == CidABC:
            raise TypeError("Can't instantiate abstract class CidABC")
        o = super().__new__(cls, *args, **kwargs)
        required = "pipe_groups nodes elements boundaries materials".split()
        if any(not hasattr(o, attr) for attr in required):
            missing = f"{[attr for attr in required if not hasattr(o, attr)]!s}"[1:-1].replace('"','').replace("'","")
            raise TypeError(f"Can't instantiate abstract class CidABC without {missing!s} attribute(s)")
        return o

@dataclass
class CidObjBase(CidABC):
    pipe_groups: Collection = field(default_factory=list)
    nodes: Collection = field(default_factory=list)
    elements: Collection = field(default_factory=list)
    boundaries: Collection = field(default_factory=list)
    materials: Collection = field(default_factory=list)
