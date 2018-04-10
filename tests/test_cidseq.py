#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidrw.cidseq` module."""
import pytest
from types import SimpleNamespace

from candejar.cidrw.cidseq import SoilMaterials, InterfMaterials
from candejar.cid.cidlineclasses import D1, D2Isotropic, D2Interface, D2Duncan


@pytest.fixture
def cidmock():
    mock = SimpleNamespace(
        nsoilmaterials=3,
        ninterfmaterials=1,
        line_objs = [D1(), D2Isotropic(), D1(), D2Duncan(), D1(), D2Duncan(), D1(model=6), D2Interface()]
    )
    return mock


def test_SoilMaterials(cidmock):
    cidmock.soilmaterials = SoilMaterials(cidmock)
    cidmock.interfmaterials = InterfMaterials(cidmock)
    assert cidmock.interfmaterials[0].model == 6
    assert cidmock.soilmaterials[0].model == 1
    assert cidmock.soilmaterials[0].model == 1
    assert 3 == len(cidmock.soilmaterials)
    assert 1 == len(cidmock.interfmaterials)
