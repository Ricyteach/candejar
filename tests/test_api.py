import yaml
from io import StringIO

from candejar import CandeObj
from candejar.cidl3 import cidl3_dict_to_candeobj_dict

SOIL = '''
4
1    0.0    0.0
2    1.0    0.0
3    1.0    1.0
4    0.0    1.0
1
1    1    2    3    4
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

def test_api():
    cobj = CandeObj(**cidl3_dict_to_candeobj_dict(yaml.safe_load(StringIO(CIDL3))))
    cobj.add_from_msh(StringIO(SOIL), name="SOIL")
    cobj.add_from_msh(StringIO(STRUCT), name="STRUCT")

