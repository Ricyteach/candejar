#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidobj` module."""

import pytest
from pathlib import Path
from candejar.cidobj.cidobj import CidObj
from candejar.cidrw.exc import CIDRWError

from tests.input_test_standards import input_test_standard1

@pytest.fixture
def cid_file_lines():
    return input_test_standard1.split("\n")

def test_blank_cid_obj():
    print()
    o = CidObj()
    print(o)
    assert o

def test_rw_cid_obj(cid_file_lines):
    print()
    o = CidObj(cid_file_lines)
    print(o)
    assert len(o.nodes) == 1471
    assert len(o.elements) == 2047
    assert len(o.boundaries) == 46
    assert len(o.materials) == 3
    assert len(o.soilmaterials) == 3
    assert len(o.interfmaterials) == 0
    cid_output_path = Path(__file__).resolve().parents[0].joinpath("output_test1.cid")
    o.save(cid_output_path, mode="w")
    assert cid_file_lines == cid_output_path.read_text().split("\n")

def test_write_blank_cid_obj():
    c = CidObj()
    p = Path(__file__).resolve().parents[0].joinpath("bad_output_test.cid")
    # raises error because sub sequences are all empty
    with pytest.raises(CIDRWError):
        c.save(p, mode="w")
