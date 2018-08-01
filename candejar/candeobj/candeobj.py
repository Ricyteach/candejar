# -*- coding: utf-8 -*-

"""The cande type objects expected by the module."""

from __future__ import annotations

import operator
from dataclasses import dataclass, InitVar, field
from pathlib import Path
from typing import Union, Type, Optional, Iterable, ClassVar, MutableMapping, Sequence, TypeVar, NamedTuple, Dict, List, \
    Counter, Any
import itertools
import shapely.geometry as geo

from . import exc
from .. import msh
from .candeseq import cande_seq_dict, PipeGroups, Nodes, Elements, PipeElements, SoilElements, InterfElements, \
    Boundaries, Materials, SoilMaterials, InterfMaterials, CompositeMaterials, Factors, NodesSection, ElementsSection, BoundariesSection
from .connections import MergedConnection, InterfaceConnection, LinkConnection, CompositeConnection, Connection, Connections, Tolerance
from .converter import NumMapsManager
from ..cid import CidLine
from ..cidrw import CidLineStr
from .parts import Node
from ..cidobjrw.cidrwabc import CidRW
from ..cidobjrw.cidobj import CidObj
from ..utilities.mapping_tools import shallow_mapify
from ..utilities.skip import skippable_len, SkipInt

T = TypeVar("T", bound="TotalDef")


class TotalDef(NamedTuple):
    """Each of these relate the sequence attribute name, total attribute name, and the other sequences attributes whose
    members contain attribute references to compute the total number of relevant objects.
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

    # sub object map sequences
    pipegroups: PipeGroups = field(default_factory=PipeGroups, repr=False)
    nodes: Nodes = field(default_factory=Nodes, repr=False)
    elements: Elements = field(default_factory=Elements, repr=False)
    boundaries: Boundaries = field(default_factory=Boundaries, repr=False)
    soilmaterials: SoilMaterials = field(default_factory=SoilMaterials, repr=False)
    interfmaterials: InterfMaterials = field(default_factory=InterfMaterials, repr=False)
    compositematerials: CompositeMaterials = field(default_factory=CompositeMaterials, repr=False)
    factors: Factors = field(default_factory=Factors, repr=False)

    # map sequence for section node connections
    connections: Connections = field(default_factory=Connections)
    # key for connection elements section
    connections_key: ClassVar[object] = object()

    # required name for initial mesh objects added
    name: InitVar[Optional[str]] = None
    section_names: ClassVar[set] = SectionNameSet()

    # additional sub object iterable properties
    @property
    def pipeelements(self):
        return PipeElements({k:v for k,v in self.elements.seq_map.items() if v and v[0].category.name=="PIPE"})

    @property
    def soilelements(self):
        return SoilElements({k:v for k,v in self.elements.seq_map.items() if v and v[0].category.name=="SOIL"})

    @property
    def interfelements(self):
        return InterfElements({k:v for k,v in self.elements.seq_map.items() if v and v[0].category.name=="INTERFACE"})

    @property
    def materials(self):
        return Materials(soil=self.soilmaterials, interface=self.interfmaterials, composite=self.compositematerials)

    def __post_init__(self, name):
        name = type(self).section_names.handle_section_name(self, name)

        cande_list_seq_kwargs = dict(pipegroups=self.pipegroups, soilmaterials=self.soilmaterials,
                                     interfmaterials=self.interfmaterials, compositematerials=self.compositematerials,
                                     factors=self.factors)

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
        """Creates a new section of standard boundaries. The nodes section can either be provided, or an existing nodes
        section referenced by name (the same name as the new boundaries section). However it is not required that the
        new boundaries section name match the nodes section name (pass a reference to and existing nodes section name
        to the nodes argument in this case).

        The problem boundary extents are assumed to be rectangular. The max and min X coordinates, and the min Y
        coordinate, define the boundaries.

        NOTE: if a new nodes section is created it is NOT added to the nodes sections automatically! This needs to be
        done separately. Might change this later?
        """

        # resolve the node section to be referenced by new boundaries section
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

        # add new boundaries section
        self.boundaries[section_name] = list()
        self.boundaries[section_name].nodes = section_nodes

        # build the defining boundaries info
        node_seq = self.boundaries[section_name].nodes
        y_min = min(node_seq, key=operator.attrgetter("y")).y
        x_min = min(node_seq, key=operator.attrgetter("x")).x
        x_max = max(node_seq, key=operator.attrgetter("x")).x

        # find and add the correct nodes to the new boundary section
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
            attr_len = skippable_len(getattr(self, total_def.seq_name))
            # TODO: handle situation when attr_len includes nodes with num set to zero because exist in another NodesSection
            attr_max = 0
            for seq_obj, sub_attrs in ((getattr(self, ch), [sub] if isinstance(sub, str) else sub)
                                         for ch, sub in total_def.attr_dict.items()):
                attr_max = max(itertools.chain([attr_max], (getattr(sub_obj, sub_attr) for sub_obj in seq_obj for sub_attr in sub_attrs)))
            setattr(self, total_def.total_name, max(attr_len, attr_max))

        # pipe group totals
        num_ctr = Counter([e.mat for e in self.pipeelements])
        for group_num, group in enumerate(self.pipegroups, 1):
            group.num = num_ctr[group_num]


    def merge_nodes(self, *nodes, converter: Dict[int, int]):
        pass


    def globalize_node_references(self, converter: NumMapsManager):
        """Re-numbers all node numbers, and references to them, based on current global node order.

        Repeated node numbers in element k and l fields are removed.
        """
        # remove repeats and reassign i,j,k,l numbers
        for seq in self.elements.seq_map.values():
            nodes_id = id(seq.nodes)
            sub_map = converter[nodes_id]
            for element in seq:
                element.remove_repeats()
                # TODO: relocate below routine to method on Element class
                for attr in "ijkl":
                    old = getattr(element, attr)
                    # skip zero entries
                    if old:
                        new = sub_map[old]
                        setattr(element, attr, new)

        # reassign boundary.node numbers
        for seq in self.boundaries.seq_map.values():
            nodes_id = id(seq.nodes)
            sub_map = converter[nodes_id]
            for boundary in seq:
                # TODO: relocate below routine to method on Boundary class
                old = boundary.node
                new = sub_map[old]
                boundary.node = new

    def globalize_node_nums(self, converter: NumMapsManager):
        """Re-numbers all node numbers based on converter."""
        start = 1

        # reset node.num attribute
        seen = set()
        for s_name, seq, sub_map in ((s_name, s, converter[id(s)].copy()) for s_name, s in self.nodes.seq_map.items()):
            for node in seq:
                old_num = node.num
                try:
                    new_num = sub_map.pop(node.num)
                except KeyError:
                    if old_num not in seen:
                        raise exc.CandeKeyError(f"{s_name!r} nodes section has no conversion for node num {old_num!r}")
                else:
                    node.num = new_num
                    seen.add(new_num)

    def globalize_element_nums(self):
        """Re-numbers all element numbers based on current global element order."""
        start = 1

        # reset element.num attribute
        element_ctr = itertools.count(start)
        for seq in self.elements.seq_map.values():
            for element, num in zip(seq, element_ctr):
                element.num = num

    def mate_sections(self, *sections: ElementsSection, tol: Optional[Union[float, Tolerance]] = None):
        """Automatically populates the connections sequence with node merges when nodes from the sections are within the
        tolerance buffer
        """
        if not isinstance(tol, Tolerance) and tol is not None:
            tol = Tolerance(tol)

        if len(sections)<2:
            raise exc.CandeValueError(f"minimum of two sections must be provided to be mated together")

        buffer = tol if tol is not None else MergedConnection.tol

        nodes_sections: List[NodesSection]
        nodes_sections = [s.nodes.copy() for s in sections]

        for curr_section_idx, curr_section in enumerate(nodes_sections):
            curr_mp = geo.shape(curr_section)
            # compare against the other sections
            compare_sections = (s for idx, s in enumerate(nodes_sections) if idx>curr_section_idx)
            for compare_section in compare_sections:
                compare_mp = geo.shape(compare_section)
                for polygon in curr_mp.buffer(buffer).intersection(compare_mp.buffer(buffer)):
                    curr_nodes = list()
                    compare_nodes = list()
                    polygon_intersects = lambda point_node: polygon.intersects(point_node[0])
                    for _, curr_node in filter(polygon_intersects, zip(curr_mp, curr_section)):
                        curr_nodes.append(curr_node)
                    for _, compare_node in filter(polygon_intersects, zip(compare_mp, compare_section)):
                        compare_nodes.append(compare_node)
                    # only add a connection if nodes from both sides fell in the polygon
                    if curr_nodes and compare_nodes:
                        merged_nodes = curr_nodes + compare_nodes
                        conn = MergedConnection(merged_nodes)  # this argument OK; pycharm can't handle dataclass inheritance yet
                        if tol is not None:
                            conn.tol = tol
                        self.connections.append(conn)

    def make_connections(self):
        """The global node numbers in the converter map are mutated so CANDE problem connections are resolved. The
        converter numbers also renumbered starting at 1. The interface elements and nodes, and link elements, are also
        created. Node num attributes are set to SkipInt() (ie, zero) if the same node already appears in another
        NodesSection.
        """
        connection_elements: List[Dict[str, Any]] = []
        conn: Connection
        for conn in self.connections:
            if not conn.category.value:
                conn: MergedConnection
                # merged connection - set num to be skipped in all sections but first
                master, *slaves = conn.items
                master.slaves = slaves
                for slave in slaves:
                    slave.num = SkipInt(slave.num)
                    slave.master = master
            else:
                conn: Union[InterfaceConnection, LinkConnection]
                # only two nodes allowed
                item: Node
                i, j = (item.num for item in conn.items)
                # create connection element
                element_ns = dict(num=0, i=i, j=j, step=conn.step, connection=conn.category.value)
                for attr in "mat death".split():
                    # some link elements don't have a material (PINNED, FIXED)
                    # interface elements don't have death
                    try:
                        element_ns[attr] = getattr(conn, attr)
                    except AttributeError:
                        pass
                # check valid connection material number if applicable (interfaces and composites only)
                if isinstance(conn, (CompositeConnection, InterfaceConnection)):
                    materials_attr = {isinstance(conn ,CompositeConnection): "compositematerials",
                                      isinstance(conn, InterfaceConnection): "interfmaterials"}[True]
                    if conn.mat-1 not in (mat.num for mat in getattr(self, materials_attr)):
                        mat_nums = [mat.num for mat in getattr(self, materials_attr)]
                        raise exc.CandeValueError(f"Mat number {conn.mat!s} was not found in the {materials_attr} list: {str(mat_nums)[1:-1]}")
                connection_elements.append(element_ns)

    def prepare(self):
        """Make CANDE problem ready for saving. Affects all elements AND all boundaries.

            1. Moves interface sections to the back of the nodes map
            2. Converts repeated node numbers to 0
            3. Updates .num attribute for nodes, elements
            4. Updates node numbers to global values
            5. Moves beam sections to the front of the elements map
            6. Updates all totals (nodes, elements, boundaries, soil/interf materials, pipe groups, steps)
        """
        # init conversion map
        node_convert_map = NumMapsManager(self.nodes)

        # change the converter map so CANDE problem connections are resolved (change conversion map target numbers)
        self.make_connections()

        if any(not conn.category.value for conn in self.connections):
            # re-number node converter to account for unused numbers after handling of merged nodes
            node_convert_map.renumber()

        if any(conn.category.value for conn in self.connections):
            # TODO: add interface node section for newly added interface connections and update interface element k values
            # TODO: move existing interface sections to back of nodes section map
            raise NotImplementedError("Non-merged connections not yet fully supported")
            # incorporate connection elements into problem
            self.elements[self.connections_key] = connection_elements

        # globalize node numbering
        self.globalize_node_nums(node_convert_map)

        # globalize node references for elements and boundaries AND remove node num repeats from element k,l fields
        self.globalize_node_references(node_convert_map)

        # move pipe element sequences to front of seq_map
        if self.elements:
            seq_map_copy = self.elements.seq_map.copy()
            self.elements.seq_map.clear()
            tuple_map = dict(pipes = [], others = [])
            for section_key, seq in seq_map_copy.items():
                key = "others"
                # if the first element is PIPE, assume all are
                if seq and seq[0].category.name=="PIPE":
                    key = "pipes"
                tuple_map[key].append((section_key, seq))
            self.elements.seq_map.update(itertools.chain(*tuple_map.values()))

        # globalize element numbering
        self.globalize_element_nums()

        # calculate and set the totals for all CANDE items
        self.update_totals()
