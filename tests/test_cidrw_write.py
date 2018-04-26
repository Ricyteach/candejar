#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidrw.write` module."""

import pytest
from pathlib import Path

from candejar.cidrw.write import file
from candejar.cidrw.exc import CIDRWError


def test_write_file(cidmock, cidmock_types, cidmock_lines):
    p: Path = Path(__file__).resolve().parents[0].joinpath("output_test.cid")
    file(cidmock, iter(cidmock_types), p, mode="w")
    assert p.read_text().split("\n") == cidmock_lines

def test_write_empty_collection(cidmock, cidmock_mismatch_types):
    p = Path(__file__).resolve().parents[0].joinpath("bad_output_test.cid")
    with pytest.raises(CIDRWError):
        file(cidmock, iter(cidmock_mismatch_types), p, mode="w")
