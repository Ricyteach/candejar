#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.nummap` module."""

import pytest
from typing import Dict, NamedTuple, List
from dataclasses import make_dataclass

from candejar.candeobj.nummap import NumMap, NumMapsManager
from candejar.utilities.skip import skippable_len, SkipInt, SkipAttrIterMixin


class SkipNumList(SkipAttrIterMixin, List):
    """Object with skippable num attributes"""
    skippable_attr = "num"


No_num = make_dataclass("No_num", [])
Has_num = make_dataclass("Has_num", [("num", int),])
Has_seq_map = make_dataclass("Has_seq_map", [("seq_map", Dict[str, List[Has_num]]),])


class NumMapCheck(NamedTuple):
    """Each instance is a check"""
    length: int
    iter_len: int
    skip_len: int
    has_nums: List[Has_num]

nummap_check_list = [
    #           length iter_len skip_len HasNum list
    NumMapCheck(3,     3,       3,       SkipNumList(Has_num(i) for i in range(3))),
    NumMapCheck(3,     3,       0,       SkipNumList(Has_num(SkipInt(i)) for i in range(3))),
]


@pytest.fixture(params=nummap_check_list)
def nummap_check(request):
    """Data used for the tests"""
    return request.param


@pytest.fixture
def num_map(nummap_check: NumMapCheck):
    """A NumMap to test"""
    return NumMap(nummap_check.has_nums)


class TestNumMap:
    """
    Given: a NumMap constructed from a NumMapCheck.has_nums list
    """

    def test_no_num_attribute(self, num_map: NumMap):
        with pytest.raises(AttributeError):
            NumMap([No_num()])

    def test_falsey(self, num_map: NumMap):
        assert not NumMap([])

    def test_truthy(self, num_map: NumMap):
        assert num_map

    def test_len(self, num_map: NumMap, nummap_check: NumMapCheck):
        assert len(num_map) == nummap_check.length

    def test_iter(self, num_map: NumMap, nummap_check: NumMapCheck):
        assert sum(1 for _ in num_map) == nummap_check.iter_len

    def test_skippable_len(self, num_map: NumMap, nummap_check: NumMapCheck):
        assert skippable_len(num_map) == nummap_check.skip_len


@pytest.fixture
def has_n_map(nummap_check):
    return Has_seq_map(seq_map=dict(x=nummap_check.has_nums))


@pytest.fixture
def no_n_map():
    return Has_seq_map(seq_map=dict(x=[No_num()]))


@pytest.fixture
def num_maps_manager(has_n_map):
    return NumMapsManager(has_n_map)


class TestNumMapsManager:

    def test_manager(self, no_n_map):
        with pytest.raises(AttributeError):
            NumMapsManager(no_n_map)

    def test_falsey(self):
        assert not NumMapsManager(Has_seq_map(dict()))

    def test_truthy(self, num_maps_manager):
        assert num_maps_manager

    def test_len(self, num_maps_manager):
        assert len(num_maps_manager) == 1