#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidrw.cidobj` module."""

import pytest
from pathlib import Path
from candejar.cidrw.cidobj import CidObj
from candejar.cidrw import write


@pytest.fixture
def cid_file_lines():
    return Path(__file__).resolve().parents[0].joinpath("input_test1.cid").read_text().split("\n")

def test_blank_cid_obj():
    print()
    o = CidObj()
    print(o)
    assert o

def test_read_cid_obj(cid_file_lines):
    print()
    o = CidObj(cid_file_lines)
    print(o)
    assert o
    assert len(o.materials) == 3
    assert len(o.soilmaterials) == 3
    assert len(o.interfmaterials) == 0

def test_write_blank_cid_obj():
    write.file(CidObj(), Path(__file__).resolve().parents[0].joinpath("output_test1.cid"))
