#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidrw.cidobj_abc` module."""
import pytest
from candejar.cidrw.cidobj_abc import CidObjBase, CidABC


def test_cidabc_subclass():
    assert CidObjBase()

def test_fail_cidabc():
    with pytest.raises(TypeError):
        assert CidABC()
