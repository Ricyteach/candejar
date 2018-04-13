#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidobjrw` module."""

import pytest
from pathlib import Path
from candejar.cidobjrw.cidobj import CidObj
from candejar.cidrw.exc import CIDRWError

def test_blank_cid_obj(cid_blank):
    assert cid_blank

def test_rw_cid_obj(cid_obj_standard, cid_standard_lines):
    assert len(cid_obj_standard.nodes) == 1471
    assert len(cid_obj_standard.elements) == 2047
    assert len(cid_obj_standard.boundaries) == 46
    assert len(cid_obj_standard.materials) == 3
    assert len(cid_obj_standard.soilmaterials) == 3
    assert len(cid_obj_standard.interfmaterials) == 0
    cid_output_path = Path(__file__).resolve().parents[0].joinpath("output_test1.cid")
    cid_obj_standard.save(cid_output_path, mode="w")
    assert cid_standard_lines == cid_output_path.read_text().split("\n")

def test_write_blank_cid_obj():
    c = CidObj()
    p = Path(__file__).resolve().parents[0].joinpath("bad_output_test.cid")
    # raises error because sub sequences are all empty
    with pytest.raises(CIDRWError):
        c.save(p, mode="w")

@pytest.mark.skip(reason="only works on local machine")
def test_open_wild_files():
    p = Path(r"S:\Uponor\19962 CANDE Analyses for Two Layer Weholite Pipes, Quebec, Canada\CANDE runs\run1.cid")
    cid = CidObj(p.read_text().split("\n"))
    assert cid
