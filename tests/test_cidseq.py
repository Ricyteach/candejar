#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidobjrw.cidseq` module."""
import pytest

from candejar.cidobjrw.cidseq import SoilMaterialSeq, InterfMaterialSeq


def test_SoilMaterialSeq(cidmock):
    cidmock.soilmaterials = SoilMaterialSeq(cidmock)
    cidmock.interfmaterials = InterfMaterialSeq(cidmock)
    assert cidmock.interfmaterials[0].model == 6
    assert cidmock.soilmaterials[0].model == 1
    assert 1 == len(cidmock.soilmaterials)
    assert 1 == len(cidmock.interfmaterials)
