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
    cande_obj = CandeObj()
    assert cande_obj
    assert not cande_obj.nodes
    assert not cande_obj.elements
    assert not cande_obj.boundaries


def test_load_blank_cidobj(cid_blank):
    cande_obj = CandeObj.load_cidobj(cid_blank)
    assert cande_obj
    assert not cande_obj.nodes
    assert not cande_obj.elements
    assert not cande_obj.boundaries


def test_load_cid_standard(cid_obj_standard, cande_obj_standard):
    assert all(getattr(cande_obj_standard, name) == getattr(cid_obj_standard, name) for name in SEQ_LINE_TYPE_TOTALS)
    assert cande_obj_standard.nodes
    assert cande_obj_standard.elements
    assert cande_obj_standard.boundaries
    assert cande_obj_standard.nodes["section1"]
    assert cande_obj_standard.elements["section1"].nodes
    assert cande_obj_standard.boundaries["section1"].nodes


def test_add_from_msh_all_obj(monkeypatch, cande_obj_standard: CandeObj, msh_all_obj: Msh):
    def mock_open(*args, **kwargs):
        return msh_all_obj
    monkeypatch.setattr(msh, "open", mock_open)
    file_name = "FAKE"
    cande_obj_standard.add_from_msh(file_name)
    assert cande_obj_standard.nodes
    assert cande_obj_standard.elements
    assert cande_obj_standard.boundaries
    assert cande_obj_standard.nodes["section1"]
    assert cande_obj_standard.elements["section1"].nodes
    assert cande_obj_standard.boundaries["section1"].nodes
    assert cande_obj_standard.nodes["section2"]
    assert cande_obj_standard.elements["section2"].nodes
    assert cande_obj_standard.boundaries["section2"].nodes


@pytest.fixture
def new_c_obj():
    c = CandeObj()
    return c


def test_update_totals(new_c_obj):
    n_attrs = "ngroups nsteps nnodes nelements".split()
    assert all(getattr(new_c_obj, attr) == v for attr, v in zip(n_attrs, (0, 0, 0, 0)))
    new_c_obj.elements["TEST"] = []
    new_c_obj.elements.append(dict(num=1, i=1, j=2, k=0, l=0, mat=1, step=1))
    new_c_obj.update_totals()
    assert all(getattr(new_c_obj, attr) == v for attr, v in zip(n_attrs, (1, 1, 2, 1)))


