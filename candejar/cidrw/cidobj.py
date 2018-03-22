# -*- coding: utf-8 -*-

"""CID object module for working with an entire cid file as a read/write object."""
from dataclasses import dataclass, field
from typing import List, Any
from ..cid.cidline import CidLine


@dataclass
class CidObj:
    lines: List[CidLine] = field(default_factory=list, repr=False, init=False)  # cid file lines
    groups: List[Any] = field(default_factory=list, repr=False, init=False)  # pipe groups
    materials: List[Any] = field(default_factory=list, repr=False, init=False)  # soil materials
    @property
    def level(self):
        return self.a1.Level

    @property
    def method(self):
        return self.a1.Method

    @property
    def mode(self):
        return self.a1.Mode

    @property
    def ngroups(self): # pipe groups
        return self.a1.NGroups

    @property
    def nsteps(self):
        return self.c2.NSteps

    @property
    def nnodes(self):
        return self.c2.NNodes

    @property
    def nelements(self):
        return self.c2.NElements

    @property
    def nbounds(self):
        return self.c2.NBounds

    @property
    def nsoil_materials(self):
        return self.c2.NSoilMaterials

    @property
    def ninterf_materials(self):
        return self.c2.NInterfMaterials

    @property
    def soil_materials(self):
        return NotImplemented

    @property
    def interf_materials(self):
        return NotImplemented
