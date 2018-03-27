#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidobj` module."""

import pytest
from pathlib import Path
from candejar.cidrw.cidobj import CidObj

@pytest.fixture
def cid_file_lines():
    return Path(__file__).resolve().parents[0].joinpath("input_test.cid").read_text().split("\n")

def test_new_cid_obj(cid_file_lines):
    assert CidObj(cid_file_lines)
