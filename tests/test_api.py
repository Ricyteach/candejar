import pytest
import candejar.cande as cande

''' Tests the API against a simple input problem (illustrated below).

SOIL SECTION    STRUCT SECTION      COMBINED SECTIONS   MATED SECTIONS
 _     _         _                   _  _  _             _ _ _
|_|   |_|       |_|                 |_||_||_|           |_|_|_|
'''

SOIL = '''
8
1    0.0    0.0
2    1.0    0.0
3    1.0    1.0
4    0.0    1.0
5    2.0    0.0
6    3.0    0.0
7    3.0    1.0
8    2.0    1.0
2
1    1    2    3    4
2    5    6    7    8
'''[1:-1]

STRUCT = '''
4
1    1.0    0.0
2    2.0    0.0
3    2.0    1.0
4    1.0    1.0
4
1    2    1    1    1
2    3    2    2    2
3    4    3    3    3
4    1    4    4    4
'''[1:-1]

CIDL3 = '''
# CANDE Level 3 problem template
# ANALYS or DESIGN
Mode: "ANALYS"
# WSD, ASD (same as WSD) or LRFD
Method: "ASD"
# number of pipe type groups
NGroups: 1
# 60 character limit
Heading: "From `candejar` by: Rick Teachey, rick@teachey.org"
# 40 character limit
Title: "Test API"
Iterations: -99
# number of load steps
NSteps: 1
NSoilMaterials: 1
NInterfMaterials: 0
# RUN or CHECK
Check: "CHECK"
# NONE, MINIMIZE, PRINT
Bandwidth: "MINIMIZE"

PipeGroups:
    # repeat this section for each pipe group
    -
        # ALUMINUM, BASIC, CONCRETE, PLASTIC, STEEL, CONRIB, CONTUBE
        Type: "BASIC"
        # number of elements in group
        Num: 4

        # B1Basic
        # ANALYS only
        # psi
        Modulus: 1100000.0
        Poissons: 0.3
        # in2/in
        Area: 1.0
        # in4/in
        I: 1.0
        # lbs/in
        Load: 0.05

        # B2Basic
        # for ANALYS mode only
        # Small Deformation: 0, Large Deformation: 1, Plus Buckling: 2
        Mode: 0

SoilMaterials:
    # repeat section for each
    -
        # material number/identifier
        Num: 1
         # 1: Isotropic, 2: Orthotropic, 3: Duncan or Selig, 4: Overburden,
         # 5: Extended Hardin, 8: MohrCoulomb
        Model: "Isotropic"
        Density: 120.0
        # User defined or "canned" names, 20 character limit
        Name: "Soil"

        # D2Isotropic:
        # psi
        Modulus: 3500.0
        Poissons: 0.3
'''[1:-1]


@pytest.fixture
def cidl3_path(tmp_path):
    """Make the CIDL3 input file"""
    path = tmp_path / "test_api.cidl3"
    path.write_text(CIDL3)
    return path


@pytest.fixture
def soil_msh_path(tmp_path):
    """Make the soil msh input file"""
    path = tmp_path / "soil.msh"
    path.write_text(SOIL)
    return path


@pytest.fixture
def structure_msh_path(tmp_path):
    """Make the structure msh input file"""
    path = tmp_path / "structure.msh"
    path.write_text(STRUCT)
    return path


class TestAPI:
    @pytest.fixture
    def candejar_obj(self, cidl3_path):
        """Fresh CandeObj to use for API tests"""
        return cande.open(cidl3_path)

    @pytest.fixture
    def candejar_obj_with_msh_added(self, candejar_obj, soil_msh_path, structure_msh_path):
        candejar_obj.add_from_msh(soil_msh_path, name="SOIL")
        candejar_obj.add_from_msh(structure_msh_path, name="STRUCT")
        return candejar_obj

    def test_msh_info(self, candejar_obj_with_msh_added):
        assert tuple(getattr(candejar_obj_with_msh_added.nodes["SOIL"][0], attr)
                     for attr in "num x y master".split()) == (1, 0.0, 0.0, None)
        assert tuple(getattr(candejar_obj_with_msh_added.nodes["STRUCT"][0], attr)
                     for attr in "num x y master".split()) == (1, 1.0, 0.0, None)
        assert tuple(getattr(candejar_obj_with_msh_added.elements["SOIL"][0], attr)
                     for attr in "i j k l mat step".split()) == (1, 2, 3, 4, 0, 0)
        assert tuple(getattr(candejar_obj_with_msh_added.elements["STRUCT"][0], attr)
                     for attr in "i j k l mat step".split()) == (2, 1, 1, 1, 0, 0)
        assert len(candejar_obj_with_msh_added.nodes) == 12
        # check direct iteration:
        assert sum(1 for _ in candejar_obj_with_msh_added.nodes) == 12
        #assert candejar_obj_with_msh_added.boundaries["SOIL"]
        #assert candejar_obj_with_msh_added.boundaries["STRUCT"]

    @pytest.fixture
    def candejar_obj_mated(self, candejar_obj_with_msh_added):
        """Establish a mated connection between sections"""
        sections = tuple(candejar_obj_with_msh_added.elements[k] for k in "SOIL STRUCT".split())
        candejar_obj_with_msh_added.mate_sections(*sections)
        return candejar_obj_with_msh_added

    def test_mated_sections(self, candejar_obj_mated):
        assert len(candejar_obj_mated.connections) == 4

    @pytest.fixture
    def candejar_obj_standard_boundaries(self, candejar_obj_mated):
        candejar_obj_mated.add_standard_boundaries(nodes=candejar_obj_mated.nodes["SOIL"])
        return candejar_obj_mated

    def test_standard_boundaries(self, candejar_obj_standard_boundaries):
        assert len(candejar_obj_standard_boundaries.boundaries) == 6

    @pytest.fixture
    def candejar_obj_ready(self, candejar_obj_standard_boundaries):
        candejar_obj_standard_boundaries.prepare()
        return candejar_obj_standard_boundaries

    def test_prepared(self, candejar_obj_ready):
        """After mated connections, some master nodes are set to a node in the other mated section"""
        assert candejar_obj_ready.nodes["STRUCT"][0].master is candejar_obj_ready.nodes["SOIL"][1]
        assert candejar_obj_ready.nodes["STRUCT"][3].master is candejar_obj_ready.nodes["SOIL"][2]
        assert len(candejar_obj_ready.nodes) == 12
        # bypass direct iteration with len():
        assert sum(1 for _ in range(len(candejar_obj_ready.nodes))) == 12
        assert sum(1 for num in range(len(candejar_obj_ready.nodes)) if candejar_obj_ready.nodes[num].master is None) == 8  # slave nodes skipped
        assert sum(1 for _ in candejar_obj_ready.nodes["STRUCT"]) == 0  # slave nodes not iterated
