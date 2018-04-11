#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidrw.write` module."""

import pytest
from pathlib import Path
from types import SimpleNamespace

from candejar.cid import A1, A2, B1Alum, B2AlumA, B1Plastic, B2Plastic, B3PlasticAGeneral, B1Steel, B2SteelA, C1, C2, C3, C4, C5, D1, D2Isotropic, D2Interface, Stop
from candejar.cidrw.write import file
from candejar.cidrw.exc import CIDRWError


output_standard_text = """                      A-1!!ANALYS   3 0  3From `pip install candejar`: Rick Teachey, rick@teachey.org   -99               
                   A-2.L3!!ALUMINUM      0
                 B-1.Alum!!10.0E6          0.3324.0E3    24.0E3          0.000.05*10E6     2    0
               B-2.Alum.A!!      0.00      0.00      0.00
                   A-2.L3!!PLASTIC       0
              B-1.Plastic!!GENERAL   HDPE          1    0
              B-2.Plastic!!                          0.00      0.00      0.30      0.00
     B-3.Plastic.A.Smooth!!      0.00      0.00      0.00      0.00
                   A-2.L3!!STEEL         0
                B-1.Steel!!29.0E6          0.3033.0E3    33.0E3          0.00      0.00    0    2    0
              B-2.Steel.A!!      0.00      0.00      0.00      0.00
                   C-1.L3!!PREP                                         
                   C-2.L3!!    0    3    1    3    0    0    0    0    1    1    1
                      D-1!!    0    1      0.00                      
            D-2.Isotropic!!      0.00      0.00
                      D-1!!L   0    6      0.00                      
            D-2.Interface!!      0.00      0.00      1.00      0.00
STOP"""


@pytest.fixture
def cidmock():
    groupmockdcts = [
        dict(type_="ALUMINUM"),
        dict(type_="PLASTIC", walltype="GENERAL"),
        dict(type_="STEEL", jointslip=0)
    ]
    soilmaterialmockdcts = [
        dict(model=1)
    ]
    interfmaterialmockdcts = [
        dict(model=6)
    ]
    cidmockdct = dict(
        level=3,
        mode="ANALYS",
        method=0,
        ngroups=3,
        pipe_groups=[SimpleNamespace(**groupmockdct) for groupmockdct in groupmockdcts],
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
        materials=[SimpleNamespace(**materialmockdct) for materialmockdcts in (soilmaterialmockdcts, interfmaterialmockdcts) for materialmockdct in materialmockdcts]
    )
    return SimpleNamespace(**cidmockdct)

@pytest.fixture
def types1():
    return (A1, A2, B1Alum, B2AlumA, A2, B1Plastic, B2Plastic, B3PlasticAGeneral, A2, B1Steel, B2SteelA,
            C1, C2,
            D1, D2Isotropic, D1, D2Interface, Stop)

def test_write_file(cidmock, types1):
    p: Path = Path(__file__).resolve().parents[0].joinpath("output_test.cid")
    file(cidmock, iter(types1), p, mode="w")
    assert p.read_text().split("\n") == output_standard_text.split("\n")

@pytest.fixture
def types2():
    return (A1, A2, B1Alum, B2AlumA, A2, B1Plastic, B2Plastic, B3PlasticAGeneral, A2, B1Steel, B2SteelA,
            C1, C2,
            C3, C3, C3, C3, C3, C3,
            C4, C4, C4, C4, C4, C4,
            C5, C5, C5,
            D1, D2Isotropic, D1, D2Interface, Stop)

def test_write_empty_collection(cidmock, types2):
    p = Path(__file__).resolve().parents[0].joinpath("bad_output_test.cid")
    with pytest.raises(CIDRWError):
        file(cidmock, iter(types2), p, mode="w")
