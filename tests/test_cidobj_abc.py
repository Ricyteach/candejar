#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidobjrw.cidobj_abc` module."""
from itertools import repeat

import pytest
from candejar.candeobj.cidobj_abc import CandeObjBase, CandeABC, CandeTypeError
from candejar.cidobjrw.names import SEQ_NAMES


@pytest.mark.skip(reason="not ready yet")
def test_cidabc_subclass():
    obj = CandeObjBase()
    assert obj

def test_fail_cidabc():
    with pytest.raises(CandeTypeError):
        assert CandeABC()

def test_fail_cidabc_child():
    Child = type("Child", (CandeABC,), {})
    with pytest.raises(CandeTypeError):
        assert Child()

def test_succeed_cidabc_child():
    Child = type("Child", (CandeABC,), dict(zip(SEQ_NAMES, repeat([]))))
    c = Child()
    assert c
