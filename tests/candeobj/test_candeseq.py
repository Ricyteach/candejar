#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.candeseq.CandeList` class."""

import pytest
import types

from candejar.candeobj.candeseq import CandeList, cande_seq_dict

def test_cande_sequence_subclass_missing_converter_error():
    with pytest.raises(AttributeError):
        class C(CandeList[int]): ...
        C()

@pytest.fixture
def C_str_holder():
    return types.new_class("C", (CandeList[str],), dict(converter = types.SimpleNamespace))

range_ = range(3)

@pytest.fixture
def list_():
    return [dict(a=i+1, b=i+2) for i in range_]

@pytest.fixture
def c_instance(C_str_holder, list_):
    return C_str_holder(list_)

def test_cande_sequence():
    with pytest.raises(AttributeError):
        CandeList()

def test_cande_sequence_subclass(C_str_holder):
    assert C_str_holder
    assert not C_str_holder()

@pytest.mark.parametrize("i", [-1, *range_, max(range_)+1])
def test_c_instance_(i, list_, c_instance):
    if i>=len(c_instance):
        with pytest.raises(IndexError):
            c_instance[i]
    else:
        assert c_instance[i]==types.SimpleNamespace(**list_[i])
        assert c_instance[i]!=list_[i]

