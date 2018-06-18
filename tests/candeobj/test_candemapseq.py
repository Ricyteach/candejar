#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.candeseq.CandeMapSequence` class."""

import pytest
import types

from candejar.candeobj.candeseq import CandeMapSequence, cande_seq_dict

@pytest.fixture
def MyDict():
    return type("MyDict", (dict,), {})

@pytest.fixture
def CSub_str_holder():
    CSub = types.new_class("CSub", (list,), {})
    CSub.converter = staticmethod(str)
    return CSub

@pytest.fixture
def C_str_holder(CSub_str_holder):
    return types.new_class("C", (CandeMapSequence[str],), dict(seq_type = CSub_str_holder))

@pytest.fixture
def unconverted_c_my_dict(MyDict):
    return MyDict(A=[], B=[1,2,3])

@pytest.fixture
def c_my_dict(MyDict, CSub_str_holder, unconverted_c_my_dict):
    d = MyDict()
    d.update(**unconverted_c_my_dict)
    for k,v in unconverted_c_my_dict.items():
        d[k] = CSub_str_holder(v)
    return d

@pytest.fixture
def unconverted_c_kwargs():
    return dict(C=[4,5,6], D=[])

@pytest.fixture
def c_kwargs(MyDict, CSub_str_holder, unconverted_c_kwargs):
    d = MyDict()
    d.update(**unconverted_c_kwargs)
    for k,v in unconverted_c_kwargs.items():
        d[k] = CSub_str_holder(v)
    return d

@pytest.fixture
def c_instance(C_str_holder, c_my_dict, c_kwargs):
    return C_str_holder(c_my_dict, **c_kwargs)

def test_cande_sequence_subclass_missing_seq_type_error():
    with pytest.raises(AttributeError):
        class C(CandeMapSequence[int]): ...
        C()

def test_cande_sequence_subclass_missing_converter_error():
    with pytest.raises(AttributeError):
        class C(CandeMapSequence[int], seq_type=list): ...
        C()

def test_c_instance_unconverted_kwargs(C_str_holder, unconverted_c_kwargs):
    assert C_str_holder(**unconverted_c_kwargs)

def test_c_instance_unconverted_dict(C_str_holder, unconverted_c_my_dict):
    assert C_str_holder(unconverted_c_my_dict)

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
    """This test is copied from test_candeseq and tweaked, so it's kind of weird; testing to make sure CandeMapSequence
    is agnostic as to whether the seq_type actually DOES anything with its members when it receives them. All CMS cares
    about is whether seq_type has a converter attribute.

    In this case CSub_str_holder has a converter but it doesn't do anything with it. So the contents aren't changed.
    """
    if int_result is None:
        with pytest.raises(IndexError):
            c_instance[i]
    else:
        assert c_instance[i]==int_result
        assert c_instance[i]!=str(int_result)

def test_make_candesequence():
    assert cande_seq_dict
