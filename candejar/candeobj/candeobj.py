# -*- coding: utf-8 -*-

"""The cande type objects expected by the module."""

from __future__ import annotations

import operator
from dataclasses import dataclass, InitVar, field
from pathlib import Path
from typing import Union, Type, Optional, Iterable, ClassVar, MutableMapping, Sequence, TypeVar, NamedTuple, Dict, List, \
    Counter

import itertools

from .. import msh
from .candeseq import cande_seq_dict, PipeGroups, Nodes, Elements, PipeElements, SoilElements, InterfElements, \
    Boundaries, Materials, SoilMaterials, InterfMaterials, Factors
from ..cid import CidLine
from ..cidrw import CidLineStr
from ..cidobjrw.cidrwabc import CidRW
from ..cidobjrw.cidobj import CidObj
from ..utilities.mapping_tools import shallow_mapify

T = TypeVar("T", bound="TotalDef")


class TotalDef(NamedTuple):
    """Each of these relate the sequence attribute name, total attribute name, and the other sequences attributes whose
    members containt attribute references to compute the total number of relevant objects.
    """
    total_name: str
    seq_name: str
    attr_dict: Dict[str, Union[str, List[str]]]

    @classmethod
    def make(cls: Type[T], seq_name: str, total_name: str, attr_dict: Dict[str, Union[str, List[str]]] = None) -> T:
        """The attr_dict argument is optional when using this factory method."""
        if attr_dict is None:
            attr_dict = dict()
        return cls(seq_name, total_name, attr_dict)


# see CandeObj.update_totals method below for explanation
CANDE_TOTAL_DEFS = (TotalDef.make("ngroups", "pipegroups", dict(pipeelements="mat")),
                    TotalDef.make("nnodes", "nodes", dict(elements=list("ijkl"), boundaries="node")),
                    TotalDef.make("nelements", "elements"),
                    TotalDef.make("nboundaries", "boundaries"),
                    TotalDef.make("nsoilmaterials", "soilmaterials", dict(soilelements="mat")),
                    TotalDef.make("ninterfmaterials", "interfmaterials", dict(interfelements="mat")),
                    TotalDef.make("nsteps", "factors", dict(elements="step", boundaries="step")),
                    )


class SectionNameSet:
    """Handles section naming."""

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


CandeObjChild = TypeVar("CandeObjChild", bound="CandeObj")


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

    # additional sub object iterable properties
    @property
    def pipeelements(self):
        return PipeElements({k:v for k,v in self.elements.seq_map.items() if v and v[0].k==0 and v[0].l==0 and v[0].joined==0})

    @property
    def soilelements(self):
        return SoilElements({k:v for k,v in self.elements.seq_map.items() if v and v[0].k!=0 and v[0].joined==0})

    @property
    def interfelements(self):
        return InterfElements({k:v for k,v in self.elements.seq_map.items() if v and v[0].joined==1})

    @property
    def materials(self):
        return Materials(soil=self.soilmaterials, interface=self.interfmaterials)

    def __post_init__(self, name):
        name = type(self).section_names.handle_section_name(self, name)

        cande_list_seq_kwargs = dict(pipegroups=self.pipegroups, soilmaterials=self.soilmaterials,
                                     interfmaterials=self.interfmaterials, factors=self.factors)
        for k, v in cande_list_seq_kwargs.items():
            cande_sub_seq = v if isinstance(v, cande_seq_dict[k]) else cande_seq_dict[k](v)
            setattr(self, k, cande_sub_seq)

        cande_map_seq_kwargs = dict(nodes=self.nodes, elements=self.elements, boundaries=self.boundaries)
        for k, v in cande_map_seq_kwargs.items():
            cande_sub_seq = v if isinstance(v, cande_seq_dict[k]) else cande_seq_dict[k]({name: v})
            setattr(self, k, cande_sub_seq)
        for seq_obj in (self.elements, self.boundaries):
            if seq_obj:
                seq_obj[name].nodes = self.nodes[name]

    @classmethod
    def load_cidobj(cls: Type[CandeObjChild], cid: CidObj) -> CandeObjChild:
        mmap: MutableMapping = shallow_mapify(cid)
        # skip properties
        mmap.pop("materials", None)
        mmap.pop("nmaterials", None)
        return cls(**mmap)

    @property
    def nmaterials(self):
        return self.nsoilmaterials + self.ninterfmaterials

    def save(self, path: Union[str, Path], mode="x"):
        """Save .cid file to the path."""
        path = Path(path).with_suffix(".cid")
        with path.open(mode):
            path.write_text("\n".join(self.iter_line_strings()))

    @classmethod
    def from_lines(cls: Type[CandeObjChild], lines: Optional[Iterable[CidLineStr]] = None,
                   line_types: Optional[Iterable[Type[CidLine]]] = None) -> CandeObjChild:
        """Construct or edit an object instance from line string and line type inputs."""
        cidobj = CidObj.from_lines(lines, line_types)
        return cls.load_cidobj(cidobj)

    def add_from_msh(self, file, *, name: Optional[str] = None, nodes: Optional[Iterable] = None):
        section_name = type(self).section_names.handle_section_name(self, name)
        msh_obj = msh.open(file)
        # handle iterable or None nodes argument
        nodes_seq = nodes if isinstance(nodes, Sequence) else list(nodes) if nodes is not None else list()
        msh_nodes_seq, msh_elements_seq, msh_boundaries_seq = (getattr(msh_obj, attr) for attr in
                                                               "nodes elements boundaries".split())
        if msh_nodes_seq and nodes_seq:
            raise ValueError("conflicting nodes sequences were provided")
        new_nodes_seq = {bool(seq): seq for seq in (msh_nodes_seq, nodes_seq)}.get(True, None)
        if new_nodes_seq:
            self.nodes[section_name] = new_nodes_seq
        for seq_name, msh_seq in zip(("elements", "boundaries"), (msh_elements_seq, msh_boundaries_seq)):
            seq_obj = getattr(self, seq_name)
            if msh_seq:
                seq_obj[section_name] = msh_seq
                if new_nodes_seq:
                    seq_obj[section_name].nodes = self.nodes[section_name]

    def add_standard_boundaries(self, name: Optional[str] = None, nodes: Optional[Iterable] = None, *, step: int = 1):
        existing_nodes = None
        if name is None:
            section_name = type(self).section_names.section_auto_name(self, name)
        else:
            section_name = name
        try:
            type(self).section_names.validate_section_name(self, section_name)
        except ValueError:
            # name exists - refer to nodes already under that name
            try:
                existing_nodes = self.nodes[section_name]
            except KeyError as e:
                if nodes is None:
                    raise KeyError(f"failed to find {section_name!r} node section") from e
        if existing_nodes is None and nodes is None:
            raise ValueError("nodes argument is required when supplying a new section name")
        if existing_nodes is not None and nodes is not None:
            raise ValueError(f"provided nodes sequence conflicts with section name")
        if nodes is None:
            section_nodes = self.nodes[section_name]
        else:
            section_nodes = nodes
        self.boundaries[section_name] = list()
        self.boundaries[section_name].nodes = section_nodes
        node_seq = self.boundaries[section_name].nodes
        y_min = min(node_seq, key=operator.attrgetter("y")).y
        x_min = min(node_seq, key=operator.attrgetter("x")).x
        x_max = max(node_seq, key=operator.attrgetter("x")).x
        for num, n in enumerate(node_seq, 1):
            d = dict()
            if n.x in (x_max, x_min):
                d.update(node=num, xcode=1)
            if n.y in (y_min,):
                d.update(node=num, ycode=1)
            if d:
                d.update(step=step)
                self.boundaries[section_name].append(d)

    def update_totals(self):
        """Computes the total number of relevant objects for all object types contained in CandeObj. The length of the
        relevant sequence is considered, as well as the highest number referenced elsewhere in the CandeObj object (if
        there are any such references). Highest number wins.

        The totals considered are:
            - pipegroups: referenced in pipeelements
            - nodes: referenced in elements and boundaries
            - elements: referenced nowhere
            - boundaries: referenced nowhere
            - soilmaterials: referenced in soilelements
            - interfmaterials: referenced in interfelements
            - steps*: referenced in elements and boundaries
        * steps is unique; if not in LRFD method, then the length of the factors sequence is ignored for computation
        """
        # top level totals
        total_def: TotalDef
        for total_def in CANDE_TOTAL_DEFS:
            attr_len = len(getattr(self, total_def.seq_name))
            attr_max = 0
            for seq_obj, sub_attrs in ((getattr(self, ch), [sub] if isinstance(sub, str) else sub)
                                         for ch, sub in total_def.attr_dict.items()):
                attr_max = max(itertools.chain([attr_max], (getattr(sub_obj, sub_attr) for sub_obj in seq_obj for sub_attr in sub_attrs)))
            setattr(self, total_def.total_name, max(attr_len, attr_max))
        # pipe group totals
        num_ctr = Counter([e.mat for e in self.pipeelements])
        for group_num, group in enumerate(self.pipegroups, 1):
            group.num = num_ctr[group_num]
