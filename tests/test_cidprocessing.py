#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidprocessing` module."""
import pytest
from types import SimpleNamespace
from candejar.cidprocessing.main import A1

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

def process(cid):
    print("\n")
    for result in A1(cid):
        print(result.__name__, end=" ")

def test_processing(cidmock):
    process(cidmock)
