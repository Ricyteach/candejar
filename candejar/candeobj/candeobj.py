# -*- coding: utf-8 -*-

"""The interface for cid type objects expected by the module."""

from __future__ import annotations
from dataclasses import dataclass, InitVar
from pathlib import Path
from typing import Mapping, Union, Sequence, Type, Optional, Iterable, ClassVar, List, MutableMapping

from .. import msh
from .candeseq import cande_seq_dict, CandeMapSequence, CandeListSequence
from ..cid import CidLine
from ..cidrw import CidLineStr
from ..cidobjrw.cidsubobj.cidsubobj import CidSubObj, CidData
from ..cidobjrw.cidrwabc import CidRW
from ..cidobjrw.cidobj import CidObj
from ..utilities.mapping_tools import shallow_mapify
from ..utilities.collections import KeyedChainView


class SectionNameSet:
    def __get__(self, instance: Optional[CandeObj], owner: Type[CandeObj]):
        if instance is not None:
            return set(k for s_name in "nodes elements boundaries".split()
                       for k in getattr(getattr(instance, s_name), "seq_map", dict()).keys())
        return self


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

    # additional, less important top-level objects (easily edited in cande GUI)
    iterations: int = -99
    title: str = ""
    check: int = 1
    bandwidth: int = 1

    # sub object iterables
    pipegroups: InitVar[CandeListSequence] = None
    nodes: InitVar[CandeMapSequence] = None
    elements: InitVar[CandeMapSequence] = None
    boundaries: InitVar[CandeMapSequence] = None
    soilmaterials: InitVar[CandeListSequence] = None
    interfmaterials: InitVar[CandeListSequence] = None
    factors: InitVar[CandeListSequence] = None

    # required name for initial mesh objects added
    name: InitVar[Optional[str]] = None
    section_names: ClassVar[set] = SectionNameSet()

    def __post_init__(self, pipegroups, nodes, elements, boundaries, soilmaterials, interfmaterials, factors, name):
        if name is None:
            name = self.section_auto_name()
        else:
            self.validate_section_name(name)
        cande_map_seq_kwargs = dict(nodes=nodes, elements=elements, boundaries=boundaries)
        cande_list_seq_kwargs = dict(pipegroups=pipegroups, soilmaterials=soilmaterials,
                                     interfmaterials=interfmaterials, factors=factors)
        for k, v in cande_map_seq_kwargs.items():
            if v is not None:
                cande_sub_seq = cande_seq_dict[k]({name: v})
            else:
                cande_sub_seq = cande_seq_dict[k]()
            setattr(self, k, cande_sub_seq)
        for k, v in cande_list_seq_kwargs.items():
            cande_sub_seq = cande_seq_dict[k](v if v is not None else ())
            setattr(self, k, cande_sub_seq)

    @classmethod
    def load_cidobj(cls, cid: Union[
        CidObj, Mapping[str, Union[CidData, Sequence[Union[CidSubObj, Mapping[str, CidData]]]]]]) -> "CandeObj":
        map: MutableMapping = shallow_mapify(cid)
        # skip properties
        map.pop("materials", None)
        map.pop("nmaterials", None)
        return cls(**map)

    @property
    def materials(self):
        return KeyedChainView(soil=self.soilmaterials, interface=self.interfmaterials)

    @property
    def nmaterials(self):
        return self.nsoilmaterials + self.ninterfmaterials

    def save(self, path: Union[str, Path], mode="x"):
        """Save .cid file to the path."""
        path = Path(path).with_suffix(".cid")
        with path.open(mode):
            path.write_text("\n".join(self.iter_line_strings()))

    @classmethod
    def from_lines(cls, lines: Optional[Iterable[CidLineStr]] = None,
                   line_types: Optional[Iterable[Type[CidLine]]] = None) -> CidRW:
        """Construct or edit an object instance from line string and line type inputs."""
        cidobj = CidObj.from_lines(lines, line_types)
        return cls.loadcid(cidobj)

    def add_from_msh(self, file, *, name: Optional[str] = None, nodes: Optional[Iterable] = None):
        if name is None:
            name = self.section_auto_name()
        else:
            self.validate_section_name(name)
        msh_obj = msh.open(file)
        new_nodes_seq, new_elements_seq = (getattr(msh_obj, attr) for attr in "nodes elements".split())
        elements_section_dict = self.elements.seq_map
        elements_section_dict[name] = new_elements_seq

    def validate_section_name(self, name: str) -> None:
        if isinstance(name, int):
            raise TypeError("integers are not allowed for mesh section name")
        names_lower = {str(n).lower() for n in self.section_names}
        if name in names_lower:
            raise ValueError(f"the section name {name} already exists")

    def section_auto_name(self, name: Optional[str] = None) -> str:
        try:
            self.validate_section_name(name)
        except ValueError:
            names = self.section_names
            names_len = len(names)
            names_lower = {str(n).lower() for n in names}
            if name is None:
                name = f"section{names_len+1}"
            while name in names_lower:
                names_len += 1
                name = f"section{names_len+1}"
        return name
