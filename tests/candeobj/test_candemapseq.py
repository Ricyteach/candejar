#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.candeseq.CandeMapSequence` class."""

import pytest
import types

from candejar.candeobj.candeseq import CandeMapSequence, cande_seq_dict

def test_cande_sequence_subclass_missing_kwarg_convert_error():
    with pytest.raises(TypeError):
        class C(CandeMapSequence[int]): ...
        C()

@pytest.fixture
def MyDict():
    return type("MyDict", (dict,), {})

@pytest.fixture
def c_my_dict(MyDict):
    return MyDict(A=[], B=[1,2,3])

@pytest.fixture
def c_kwargs():
    return dict(C=[4,5,6], D=[])

@pytest.fixture
def C_str_holder():
    return types.new_class("C", (CandeMapSequence[str],), dict(kwarg_convert = str))

@pytest.fixture
def c_instance(C_str_holder, c_my_dict, c_kwargs):
    return C_str_holder(c_my_dict, **c_kwargs)

def test_cande_sequence():
    with pytest.raises(TypeError):
        CandeMapSequence()

def test_cande_sequence_subclass(C_str_holder):
    assert C_str_holder
    assert not C_str_holder()

def test_c_instance_seqmap_type(c_instance, MyDict):
    assert type(c_instance.seq_map) == MyDict

@pytest.mark.parametrize("i, int_result", [
    (-1, 6),
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6),
    (7, None),
])
def test_c_instance_(i, int_result, c_instance):
    if int_result is None:
        with pytest.raises(IndexError):
            c_instance[i]
    else:
        assert c_instance[i]==str(int_result)
        assert c_instance[i]!=int(int_result)

def test_make_candesequence():
    assert cande_seq_dict
