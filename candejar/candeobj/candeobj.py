# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import MutableMapping, Mapping, Union, Sequence

from ..cidobjrw.cidsubobj.cidsubobj import CidSubObj, CidData
from ..cidobjrw.names import ALL_SEQ_NAMES
from ..utilities.dataclasses import shallow_mapify
from ..utilities.collections import ChainSequence
from ..cidobjrw.cidobj import CidObj


class CandeError(Exception):
    pass


class IncompleteCandeObjError(CandeError):
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
    pipe_groups: Sequence = field(default_factory=list)
    nodes: Sequence = field(default_factory=list)
    elements: Sequence = field(default_factory=list)
    boundaries: Sequence = field(default_factory=list)
    soilmaterials: Sequence = field(default_factory=list)
    interfmaterials: Sequence = field(default_factory=list)
    factors: Sequence = field(default_factory=list)

    @classmethod
    def loadcid(cls, cid: Union[CidObj, Mapping[str,Union[CidData, Sequence[Union[CidSubObj, Mapping[str, CidData]]]]]]) -> "CandeObj":
        map: MutableMapping = shallow_mapify(cid)
        map.pop("materials",None)
        for seq_k in ALL_SEQ_NAMES:
            try:
                seq = map[seq_k]
            except KeyError:
                # materials is a property
                if seq_k == "materials":
                    continue
                seq = []
            map[seq_k] = shallow_mapify(seq)
        return cls(**map)

    @property
    def materials(self):
        return ChainSequence(self.soilmaterials, self.interfmaterials)

    @property
    def nmaterials(self):
        return self.nsoilmaterials + self.ninterfmaterials

    def save(self, path: Union[str, Path], mode="x"):
        """Save .cid file to the path."""
        path = Path(path).with_suffix(".cid")
        with path.open(mode):
            path.write_text("\n".join(self.iter_lines()))

