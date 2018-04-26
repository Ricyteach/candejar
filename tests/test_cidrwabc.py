#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidobjrw.cidrwabc` module."""
import pytest

from candejar.cidobjrw.cidrwabc import CidRW
from candejar.cidobjrw.exc import CidRWSubclassSignatureError

def test_subclass():
    class Child(CidRW):
        @classmethod
        def from_lines(cls):
            pass
    assert Child()

def test_subclass_fail_on_no_default_arguments():
    with pytest.raises(CidRWSubclassSignatureError):
        class _(CidRW):
            def __init__(self, _): ...
            def from_lines(self): ...

def test_subclass_fail_on_no_from_lines_method():
    with pytest.raises(TypeError):
        class Child(CidRW):
            pass
        Child()
