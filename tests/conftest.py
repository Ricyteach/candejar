#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Fixtures for use across the testing suite"""
import pytest

from candejar.cidobjrw.cidobj import CidObj
from tests.input_test_standards import input_test_standard1

@pytest.fixture
def cid_standard_lines():
    return input_test_standard1.split("\n")

@pytest.fixture
def cid_obj_standard(cid_standard_lines):
    print()
    o = CidObj(cid_standard_lines)
    print(o)
    return o

@pytest.fixture
def cid_blank():
    print()
    o = CidObj()
    print(o)
    return o
