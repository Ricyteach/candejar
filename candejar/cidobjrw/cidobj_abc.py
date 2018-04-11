# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Collection


@dataclass
class CidABC(metaclass=ABCMeta):
    @abstractmethod
    def pipe_groups(self):...
    @abstractmethod
    def nodes(self):...
    @abstractmethod
    def elements(self):...
    @abstractmethod
    def boundaries(self):...
    @abstractmethod
    def materials(self):...

@dataclass
class CidObjBase(CidABC):
    # top level objects
    mode: str = field(default="ANALYS")  # ANALYS or DESIGN
    level: int = field(default=3)  # 1, 2, 3
    method: int = field(default=0)  # 0=WSD, 1=LRFD
    ngroups: int = field(default=0)  # pipe groups
    heading: str = field(default="From `pip install candejar`: Rick Teachey, rick@teachey.org")
    iterations: int = field(default=-99)
    title: str = field(default="")
    check: int = field(default=1)
    nsteps: int = field(default=0)  # load steps
    nnodes: int = field(default=0)
    nelements: int = field(default=0)
    nboundaries: int = field(default=0)
    nsoilmaterials: int = field(default=0)
    ninterfmaterials: int = field(default=0)

    # sequences of sub objects
    pipe_groups: Collection = field(default_factory=list)
    nodes: Collection = field(default_factory=list)
    elements: Collection = field(default_factory=list)
    boundaries: Collection = field(default_factory=list)
    materials: Collection = field(default_factory=list)
    factors: Collection = field(default_factory=list)
