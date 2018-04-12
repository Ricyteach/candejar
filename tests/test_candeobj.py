#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj` module."""

import pytest
from candejar.candeobj.candeobj import CandeObj
from candejar.cidobjrw.cidobj import CidObj

def test_candebase():
    assert CandeObj()

def test_load_cidobj():
    assert CandeObj.loadcid(CidObj())
