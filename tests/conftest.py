#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Fixtures for use across the testing suite"""
import pytest
from types import SimpleNamespace

from candejar.cidobjrw.cidobj import CidObj
from candejar.cid.cidlineclasses import A1, A2, B1Alum, B2AlumA, A2, B1Plastic, B2Plastic, B3PlasticAGeneral, A2, \
    B1Steel, B2SteelA,C1, C2, C3, C4, C5, D1, D2Isotropic, D1, D2Interface, Stop
from tests.cid_file_test_standards import standard_lines, cidmock_standard_lines

@pytest.fixture(scope="session")
def cid_standard_lines():
    return standard_lines.split("\n")

@pytest.fixture(scope="session")
def cid_obj_standard(cid_standard_lines):
    print()
    o = CidObj(cid_standard_lines)
    print(o)
    return o

@pytest.fixture(scope="session")
def cid_blank():
    print()
    o = CidObj()
    print(o)
    return o

@pytest.fixture(scope="session")
def cidmock_lines():
    lines = cidmock_standard_lines.split("\n")
    return lines

@pytest.fixture(scope="session")
def cidmock_types():
    return (A1, A2, B1Alum, B2AlumA, A2, B1Plastic, B2Plastic, B3PlasticAGeneral, A2, B1Steel, B2SteelA,
            C1, C2,
            D1, D2Isotropic, D1, D2Interface, Stop)

@pytest.fixture(scope="session")
def cidmock_mismatch_types():
    return (A1, A2, B1Alum, B2AlumA, A2, B1Plastic, B2Plastic, B3PlasticAGeneral, A2, B1Steel, B2SteelA,
            C1, C2,
            C3, C3, C3, C3, C3, C3,
            C4, C4, C4, C4, C4, C4,
            C5, C5, C5,
            D1, D2Isotropic, D1, D2Interface, Stop)

@pytest.fixture(scope="session")
def cidmock(cidmock_types):
    groupmocks = [
        SimpleNamespace(type_="ALUMINUM"),
        SimpleNamespace(type_="PLASTIC", walltype="GENERAL"),
        SimpleNamespace(type_="STEEL", jointslip=0)
    ]
    soilmaterialmocks = [
        SimpleNamespace(model=1)
    ]
    interfmaterialmocks = [
        SimpleNamespace(model=6)
    ]
    mock = SimpleNamespace(
        level=3,
        mode="ANALYS",
        method=0,
        ngroups=3,
        pipe_groups=groupmocks,
        nsteps=0,
        nnodes=0,
        nelements=0,
        nboundaries=0,
        nsoilmaterials=1,
        ninterfmaterials=1,
        nmaterials=2,  # nmaterials is required in order to write a cid object
        nodes=[],
        elements=[],
        boundaries=[],
        materials=soilmaterialmocks+interfmaterialmocks,
        line_objs = [cls() for cls in cidmock_types]
    )
    mock.line_objs[-3] = D1(model=6)
    return mock
