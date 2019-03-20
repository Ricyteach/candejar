#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.candeseq.CandeList` class."""

import pytest
import types

from candejar.candeobj.candeseq import CandeList, CandeChainMap, CandeChainMapKeyError, CandeChainMapTypeError,\
    CandeChainMapError, CandeChainMapValueError


class TestCandeChainMap:

    @pytest.fixture
    def ccm(self):
        return CandeChainMap(LALA={1:"a", 2:"b"}, FOO={}, BAR={}, BAZ={})

    def test_change_value(self, ccm):
        ccm[1]="A"

    def test_add_section(self, ccm):
        d = {1:"c", 2:"d"}
        ccm["BUZZ"] = d
        assert ccm.maps[-1] is d

    def test_add_value(self, ccm):
        ccm["FOO"][1] = "c"
        assert ccm.maps[2][1] == "c"

    def test_del_section(self, ccm):
        del_map = ccm["LALA"]
        assert del_map in ccm.maps[0].values()
        del ccm["LALA"]
        assert len(ccm.maps) == 4
        assert len(ccm.maps[0]) == 3
        assert del_map not in ccm.maps[0].values()

    def test_pop_number(self, ccm):
        assert ccm.pop(2) == "b"

    def test_pop_section(self, ccm):
        d = ccm.maps[0]["FOO"]
        assert any(d is v for v in ccm.maps[0].values())
        assert ccm.pop("FOO") is d
        assert all(d is not v for v in ccm.maps[0].values())

    def test_pop_item(self, ccm):
        k = "BAZ"
        d = ccm.maps[0][k]
        assert ccm.popitem() == (k, d)

    def test_bad_dict_key(self, ccm):
        with pytest.raises(CandeChainMapValueError):
            ccm["BUZZ"] = dict(a=None)

    def test_no_add_object(self, ccm):
        with pytest.raises(CandeChainMapKeyError):
            ccm[0] = None

    def test_bad_section_name(self, ccm):
        with pytest.raises(CandeChainMapTypeError):
            ccm[None] = None

    def test_bad_section_type(self, ccm):
        with pytest.raises(CandeChainMapTypeError):
            ccm["BUZZ"] = None

    def test_bad_state_delete(self, ccm):
        del ccm.maps[-1]
        with pytest.raises(CandeChainMapError):
            del ccm["BAZ"]


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

