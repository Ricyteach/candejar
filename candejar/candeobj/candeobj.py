# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""
from dataclasses import dataclass, field, asdict
from typing import Collection

from ..utilities.collections import ChainSequence
from ..cidobjrw.cidobj import CidObj


class CandeError(Exception):
    pass


@dataclass
class CandeObj:
    # top level objects
    mode: str = field(default="ANALYS")  # ANALYS or DESIGN
    level: int = field(default=3)  # 1, 2, 3
    method: int = field(default=0)  # 0=WSD, 1=LRFD
    ngroups: int = field(default=0)  # pipe groups
    heading: str = field(default="From `pip install candejar`: "
                                 "Rick Teachey, rick@teachey.org")
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
    soilmaterials: Collection = field(default_factory=list)
    interfmaterials: Collection = field(default_factory=list)
    factors: Collection = field(default_factory=list)

    @classmethod
    def loadcid(cls, cid: CidObj):
        d = asdict(cid)
        d.pop("materials")
        return cls(**d)

    @property
    def materials(self):
        return ChainSequence(self.soilmaterials, self.interfmaterials)
