#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.Material` subclasses."""

import pytest

from candejar.candeobj.materials import Isotropic, DuncanSelig, MohrCoulomb, Interface
from candejar.candeobj.exc import CandeValueError


def test_wrong_material_num():
    with pytest.raises(CandeValueError):
        Isotropic(2)
        DuncanSelig(2)
        MohrCoulomb(2)
        Interface(2)

def test_canned_duncan_selig():
    assert DuncanSelig.duncan
    assert DuncanSelig.duncan.CL90
    assert DuncanSelig.selig
    assert DuncanSelig.selig.CL90
