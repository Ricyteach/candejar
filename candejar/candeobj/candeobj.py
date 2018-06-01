# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

from dataclasses import dataclass, InitVar
from pathlib import Path
from typing import Mapping, Union, Sequence, Type, Optional, Iterable

from ..cid import CidLine
from ..cidrw import CidLineStr
from ..cidobjrw.cidsubobj.cidsubobj import CidSubObj, CidData
from ..cidobjrw.names import ALL_SEQ_NAMES
from ..cidobjrw.cidrwabc import CidRW
from ..cidobjrw.cidobj import CidObj
from ..utilities.dataclasses import shallow_mapify
from ..utilities.collections import ChainSequence


class KeyedChainViewer:
    def __init__(self, *iterable_mapping: Mapping[str,Iterable]) -> None:
        pass

@dataclass
class CandeObj(CidRW):
    """The interface for .cid file representation objects."""
    # top level objects
    mode: str = "ANALYS"  # ANALYS or DESIGN
    level: int = 3  # 1, 2, 3
    method: int = 0  # 0=WSD, 1=LRFD
    ngroups: int = 0  # pipe groups
    heading: str = "From `pip install candejar`: Rick Teachey, rick@teachey.org"
    nsteps: int = 0  # load steps
    nnodes: int = 0
    nelements: int = 0
    nboundaries: int = 0
    nsoilmaterials: int = 0
    ninterfmaterials: int = 0

    # more less important top level objects (easily edited in cande GUI)
    iterations: int = -99
    title: str = ""
    check: int = 1
    bandwidth: int = 1

    # sub object iterables
    pipegroups: InitVar[Optional[Iterable]] = None
    nodes: InitVar[Optional[Iterable]] = None
    elements: InitVar[Optional[Iterable]] = None
    boundaries: InitVar[Optional[Iterable]] = None
    soilmaterials: InitVar[Optional[Iterable]] = None
    interfmaterials: InitVar[Optional[Iterable]] = None
    factors: InitVar[Optional[Iterable]] = None

    def __post_init__(self, pipegroups, nodes, elements, boundaries, soilmaterials, interfmaterials, factors):
        kwargs = dict(pipegroups=pipegroups, nodes=nodes, elements=elements, boundaries=boundaries,
                      soilmaterials=soilmaterials, interfmaterials=interfmaterials, factors=factors)
        for k,v in kwargs.items():
            # TODO: change `list` below to a better data structure?
            cande_sub_seq = list(v if v is not None else ())
            setattr(self, k, cande_sub_seq)

    @classmethod
    def load_cidobj(cls, cid: Union[CidObj, Mapping[str,Union[CidData, Sequence[Union[CidSubObj, Mapping[str, CidData]]]]]]) -> "CandeObj":
        map = shallow_mapify(cid)
        map.pop("materials",None)
        map.pop("nmaterials",None)
        for seq_k in ALL_SEQ_NAMES:
            try:
                seq = map[seq_k]
            except KeyError:
                # skip properties
                if seq_k in ("materials", "nmaterials"):
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
            path.write_text("\n".join(self.iter_line_strings()))

    @classmethod
    def from_lines(cls, lines: Optional[Iterable[CidLineStr]]=None,
                         line_types: Optional[Iterable[Type[CidLine]]]=None) -> CidRW:
        """Construct or edit an object instance from line string and line type inputs."""
        cidobj = CidObj.from_lines(lines, line_types)
        return cls.loadcid(cidobj)
