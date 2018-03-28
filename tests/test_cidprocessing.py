#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidprocessing` module."""
import pytest
from types import SimpleNamespace
from candejar.cidprocessing.main import process

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

def process_(cid):
    for result in process(cid):
        yield result.__name__

def test_processing(cidmock):
    names = " ".join(process_(cidmock))
    assert names[:5] == "A1 A2"
    print(f"\n{names}")
