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
        dict(type_="PLASTIC", WallType="GENERAL"),
        dict(type_="STEEL", jointslip=True, varytravel=True)
    ]
    soilmaterialmockdcts = [
        dict(model=1)
    ]
    interfmaterialmockdcts = [
        dict(model=7)
    ]
    cidmockdct = dict(
        level=3,
        mode="ANALYS",
        method=0,
        ngroups=3,
        groups=[SimpleNamespace(**groupmockdct) for groupmockdct in groupmockdcts],
        nsteps=2,
        nnodes=6,
        nelements=6,
        nboundaries=3,
        nsoilmaterials=1,
        soilmaterials=[SimpleNamespace(**soilmaterialmockdct) for soilmaterialmockdct in soilmaterialmockdcts],
        ninterfmaterials=2,
        interfmaterials=[SimpleNamespace(**interfmaterialmockdct) for interfmaterialmockdct in interfmaterialmockdcts]
    )
    return SimpleNamespace(**cidmockdct)

def process_(cid):
    for result in process(cid):
        yield result.__name__

def test_processing(cidmock):
    names = " ".join(process_(cidmock))
    assert names[:5] == "A1 A2"
    print(f"\n{names}")
