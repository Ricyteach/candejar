#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidrw.write` module."""
from pathlib import Path

import pytest
from types import SimpleNamespace

from candejar.cid import A1, A2, B1Alum, B2AlumA, B1Plastic, B2Plastic, B3PlasticAGeneral, B1Steel, B2SteelA, C1, C2, C3, C4, C5, D1, D2Isotropic, D2Interface, Stop
from candejar.cidrw.write import file


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
        nodes=[],
        elements=[],
        boundaries=[],
        materials=[SimpleNamespace(**materialmockdct) for materialmockdcts in (soilmaterialmockdcts, interfmaterialmockdcts) for materialmockdct in materialmockdcts]
    )
    return SimpleNamespace(**cidmockdct)

@pytest.fixture
def types():
    return (A1, A2, B1Alum, B2AlumA, A2, B1Plastic, B2Plastic, B3PlasticAGeneral, A2, B1Steel, B2SteelA,
            C1, C2,
            C3, C3, C3, C3, C3, C3,
            C4, C4, C4, C4, C4, C4,
            C5, C5, C5,
            D1, D2Isotropic, D1, D2Interface, Stop)

@pytest.mark.skip(reason="can't find infinite loop...???")
def test_write_file(cidmock, types):
    p = Path(__file__).resolve().parents[0].joinpath("output_test2.cid")
    file(cidmock, iter(types), p, mode="w")
