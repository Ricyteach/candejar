# -*- coding: utf-8 -*-

"""The cande type objects expected by the module."""

from __future__ import annotations
from dataclasses import dataclass, InitVar, field
from pathlib import Path
from typing import Union, Type, Optional, Iterable, ClassVar, MutableMapping

from .. import msh
from .candeseq import cande_seq_dict, PipeGroups, Nodes, Elements, Boundaries, SoilMaterials, InterfMaterials, Factors
from ..cid import CidLine
from ..cidrw import CidLineStr
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

    @staticmethod
    def validate_section_name(instance: CandeObj, name: str) -> None:
        """Make sure supplied section name follows the rules.

        Rules: no integers allowed, no duplicate section names allowed
        """
        if isinstance(name, int):
            raise TypeError("integers are not allowed for mesh section name")
        names_lower = {str(n).lower() for n in instance.section_names}
        if name in names_lower:
            raise ValueError(f"the section name {name} already exists")

    @staticmethod
    def section_auto_name(instance: CandeObj, name: Optional[str] = None) -> str:
        """Produce a section name that doesn't conflict with existing names

        Auto-names are produces in sequence, e.g. section1, section2, etc.

        Cardinal number determined based on current number of sections. Upper/lowercase is ignored for checking against
        existing names (i.e., if ONLY Section2 exists, the next section will not be section2 but section3).
        """
        names = instance.section_names
        names_len = len(names)
        if name is None:
            name = f"section{names_len+1}"
        try:
            SectionNameSet.validate_section_name(instance, name)
        except ValueError:
            names_lower = {str(n).lower() for n in names}
            while name in names_lower:
                names_len += 1
                name = f"section{names_len+1}"
        return name

    @staticmethod
    def handle_section_name(instance: CandeObj, name: Optional[str]) -> str:
        if name is None:
            name = SectionNameSet.section_auto_name(instance, name)
        else:
            SectionNameSet.validate_section_name(instance, name)
        return name


@dataclass
class CandeObj(CidRW):
    """For cande problem representation objects."""
    # top level objects
    mode: str = "ANALYS"  # ANALYS or DESIGN
    level: int = 3  # 1, 2, 3 (only 3 currently supported)
    method: int = 0  # 0=WSD, 1=LRFD
    ngroups: int = 0  # pipe groups
    heading: str = 'From "candejar" by Rick Teachey, rick@teachey.org'
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
    pipegroups: PipeGroups = field(default_factory=PipeGroups, repr=False)
    nodes: Nodes = field(default_factory=Nodes, repr=False)
    elements: Elements = field(default_factory=Elements, repr=False)
    boundaries: Boundaries = field(default_factory=Boundaries, repr=False)
    soilmaterials: SoilMaterials = field(default_factory=SoilMaterials, repr=False)
    interfmaterials: InterfMaterials = field(default_factory=InterfMaterials, repr=False)
    factors: Factors = field(default_factory=Factors, repr=False)

    # required name for initial mesh objects added
    name: InitVar[Optional[str]] = None
    section_names: ClassVar[set] = SectionNameSet()

    def __post_init__(self, name):
        name = type(self).section_names.handle_section_name(self, name)
        cande_map_seq_kwargs = dict(nodes=self.nodes, elements=self.elements, boundaries=self.boundaries)
        cande_list_seq_kwargs = dict(pipegroups=self.pipegroups, soilmaterials=self.soilmaterials,
                                     interfmaterials=self.interfmaterials, factors=self.factors)
        for k, v in cande_map_seq_kwargs.items():
            if not isinstance(v, cande_seq_dict[k]):
                cande_sub_seq = cande_seq_dict[k]({name: list(v)})
                setattr(self, k, cande_sub_seq)
        for k, v in cande_list_seq_kwargs.items():
            if not isinstance(v, cande_seq_dict[k]):
                cande_sub_seq = cande_seq_dict[k](list(v))
                setattr(self, k, cande_sub_seq)

    @classmethod
    def load_cidobj(cls, cid: CidObj) -> CandeObj:
        mmap: MutableMapping = shallow_mapify(cid)
        # skip properties
        mmap.pop("materials", None)
        mmap.pop("nmaterials", None)
        return cls(**mmap)

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
                   line_types: Optional[Iterable[Type[CidLine]]] = None) -> CandeObj:
        """Construct or edit an object instance from line string and line type inputs."""
        cidobj = CidObj.from_lines(lines, line_types)
        return cls.load_cidobj(cidobj)

    def add_from_msh(self, file, *, name: Optional[str] = None, nodes: Optional[Iterable] = None):
        name = type(self).section_names.handle_section_name(self, name)
        msh_obj = msh.open(file)
        nodes_seq = nodes if nodes is not None else list()
        msh_nodes_seq, msh_elements_seq, msh_boundaries_seq = (getattr(msh_obj, attr) for attr in
                                                               "nodes elements boundaries".split())
        if msh_nodes_seq and nodes_seq:
            raise ValueError("conflicting nodes sequences were provided")
        new_nodes_seq = {bool(seq): seq for seq in (msh_nodes_seq, nodes_seq)}.get(True, None)
        if msh_elements_seq:
            self.elements[name] = msh_elements_seq
        if msh_boundaries_seq:
            self.boundaries[name] = msh_boundaries_seq
        if new_nodes_seq:
            self.nodes[name] = new_nodes_seq
            self.elements[name].nodes = self.nodes[name]
        else:
            self.elements[name].nodes = self.nodes
        # TODO: handle boundaries
