#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidobjrw.cidobj_abc` module."""
import pytest
from candejar.cidobjrw.cidobj_abc import CidObjBase, CidABC


def test_cidabc_subclass():
    obj = CidObjBase()
    assert obj

def test_fail_cidabc():
    with pytest.raises(TypeError):
        assert CidABC()
