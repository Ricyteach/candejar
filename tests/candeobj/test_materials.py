#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.Material` subclasses."""

import pytest

from candejar.candeobj.materials import Isotropic, MohrCoulomb, Interface
from candejar.candeobj.duncanselig import  DuncanSelig, Duncan, Selig, \
    DuncanCanned, SeligCanned
from candejar.candeobj.exc import CandeValueError

def test_wrong_material_num():
    with pytest.raises(CandeValueError):
        Isotropic(2)
        DuncanSelig(2)
        MohrCoulomb(2)
        Interface(2)

def test_canned_duncan_selig():
    assert Duncan.CL90()
    assert Selig.CL90()
    assert DuncanCanned.CL90()
    assert SeligCanned.CL90()
