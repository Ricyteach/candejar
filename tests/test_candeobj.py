#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj` module."""

from candejar.candeobj.candeobj import CandeObj
from candejar.cidobjrw.cidobj import CidObj

def test_candebase():
    assert CandeObj()

def test_load_blank_cidobj(cid_blank):
    assert CandeObj.loadcid(cid_blank)

def test_load_cid_standard(cid_obj_standard):
    assert CandeObj.loadcid(cid_obj_standard)
