#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj` module."""

import pytest

from candejar import msh
from candejar.candeobj.candeobj import CandeObj
from candejar.cidobjrw.names import SEQ_LINE_TYPE_TOTALS
from candejar.msh import Msh


@pytest.fixture
def cande_obj_standard(cid_obj_standard):
    cobj = CandeObj.load_cidobj(cid_obj_standard)
    return cobj


def test_candebase():
    assert CandeObj()


def test_load_blank_cidobj(cid_blank):
    assert CandeObj.load_cidobj(cid_blank)


def test_load_cid_standard(cid_obj_standard, cande_obj_standard):
    assert all(getattr(cande_obj_standard, name) == getattr(cid_obj_standard, name) for name in SEQ_LINE_TYPE_TOTALS)


def test_add_from_msh_all_obj(monkeypatch, cande_obj_standard: CandeObj, msh_all_obj: Msh):
    def mock_open(*args, **kwargs):
        return msh_all_obj
    monkeypatch.setattr(msh, "open", mock_open)
    file_name = "FAKE"
    cande_obj_standard.add_from_msh(file_name)
    assert cande_obj_standard.nodes
    assert cande_obj_standard.elements
    assert cande_obj_standard.boundaries
    assert cande_obj_standard.nodes["section2"]
    assert cande_obj_standard.elements["section2"].nodes
    assert cande_obj_standard.boundaries["section2"].nodes
