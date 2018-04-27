#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj` module."""

from candejar.candeobj.candeobj import CandeObj
from candejar.cidobjrw.names import SEQ_LINE_TYPE_TOTALS

def test_candebase():
    assert CandeObj()

def test_load_blank_cidobj(cid_blank):
    assert CandeObj.loadcid(cid_blank)

def test_load_cid_standard(cid_obj_standard):
    cobj = CandeObj.loadcid(cid_obj_standard)
    assert all(getattr(cobj,name) == getattr(cid_obj_standard, name) for name in SEQ_LINE_TYPE_TOTALS)
