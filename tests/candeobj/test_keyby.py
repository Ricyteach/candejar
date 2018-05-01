#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.keyby` module."""

import pytest

from candejar.candeobj.pipe_groups import Basic
from candejar.candeobj.keyby import key_by_cid_linetype

@pytest.fixture
def XYZ():
    return tuple(type(s, (), {}) for s in "XYZ")

@pytest.fixture
def Class1(XYZ):
    X,Y,Z = XYZ
    return type("Class1", (), dict(type_key=X))

@pytest.fixture
def Class2(XYZ, Class1):
    X,Y,Z = XYZ
    return type("Class2", (Class1,), dict(type_key=Y))

@pytest.fixture
def Class3(XYZ, Class2):
    X,Y,Z = XYZ
    return type("Class3", (Class2,), dict(type_key=Z))

def test_key_by_cid_linetype(Class1, Class3, XYZ):
    k=key_by_cid_linetype(Class1)(Class3)
    assert k == XYZ

def test_Basic_subclasses():
    Basic
