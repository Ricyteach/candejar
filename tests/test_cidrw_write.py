#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidrw.write` module."""
from pathlib import Path

import pytest
from types import SimpleNamespace

from candejar.cid import A1, A2, C1, C2, C3, C4, C5, D1, D2Isotropic, E1, Stop
from candejar.cidrw.write import file


@pytest.fixture
def cidmock():
    groupmockdcts = [
        dict(type_="ALUMINUM"),
        dict(type_="PLASTIC", walltype="GENERAL"),
        dict(type_="STEEL", jointslip=True, varytravel=True)
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
        nsteps=2,
        nnodes=6,
        nelements=6,
        nboundaries=3,
        nsoilmaterials=1,
        ninterfmaterials=1,
        materials=[SimpleNamespace(**materialmockdct) for materialmockdcts in (soilmaterialmockdcts, interfmaterialmockdcts) for materialmockdct in materialmockdcts]
    )
    return SimpleNamespace(**cidmockdct)

@pytest.fixture
def types():
    return (A1, A2, C1, C2, C3, C4, C5, D1, D2Isotropic, Stop)

def test_write_file(cidmock, types):
    p = Path(__file__).resolve().parents[0].joinpath("output_test2.cid")
    file(cidmock, iter(types), p, mode="w")
