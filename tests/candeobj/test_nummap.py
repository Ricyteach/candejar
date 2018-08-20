#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.nummap` module."""
import itertools

import pytest
from typing import Dict, NamedTuple, List
from dataclasses import make_dataclass

from candejar.candeobj import exc
from candejar.candeobj.nummap import NumMap, NumMapsManager
from candejar.utilities.skip import SkipInt, SkipAttrIterMixin


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
    skippable_len: int
    bad_key: int
    has_nums: List[Has_num]


NUMMAP_CHECKS_TOTAL = 2
nummap_check_ids = ("no skippable objects", "skippable objects included")


@pytest.fixture(scope="module")
def nummap_check_cases():
    global NUMMAP_CHECKS_TOTAL
    TOTAL = NUMMAP_CHECKS_TOTAL
    try:
        assert len(nummap_check_ids) == NUMMAP_CHECKS_TOTAL
        NUMMAP_CHECKS_TOTAL = 0
        yield
        assert NUMMAP_CHECKS_TOTAL == TOTAL
    except AssertionError:
        raise Exception("check NUMMAP_CHECKS_TOTAL value")


@pytest.fixture(params=range(NUMMAP_CHECKS_TOTAL), ids=lambda param: nummap_check_ids[param])
def nummap_check(request, nummap_check_cases):
    """Data used for the tests"""
    global NUMMAP_CHECKS_TOTAL
    NUMMAP_CHECKS_TOTAL = max(NUMMAP_CHECKS_TOTAL, request.param+1)
    #                  len i_len s_len bad_k HasNum list
    if request.param == 0:
        return NumMapCheck(3, 3, 3, 10, SkipNumList(Has_num(i) for i in range(3)))
    elif request.param == 1:
        return NumMapCheck(3, 3, 0, 10, SkipNumList(Has_num(SkipInt(i)) for i in range(3)))
    else:
        pass


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

    def test_set_bad_key(self, num_map: NumMap, nummap_check: NumMapCheck):
        with pytest.raises(exc.CandeKeyError):
            num_map[nummap_check.bad_key] = None

    def test_copy(self, num_map: NumMap):
        copy = num_map.copy()
        assert copy is not num_map
        assert copy.section is num_map.section
        assert copy._d is not num_map._d
        assert copy._d == num_map._d

    def test_renumber(self, num_map: NumMap):
        num_map.renumber(10)
        assert all(a.num==b for a,b in zip(num_map.values(), itertools.count(10)))

    def test_len(self, num_map: NumMap, nummap_check: NumMapCheck):
        assert len(num_map) == nummap_check.length

    def test_iter(self, num_map: NumMap, nummap_check: NumMapCheck):
        assert sum(1 for _ in num_map) == nummap_check.iter_len


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

    def test_truthy(self, num_maps_manager: NumMapsManager):
        assert num_maps_manager

    def test_len(self, num_maps_manager: NumMapsManager):
        assert len(num_maps_manager) == 1

    def test_renumber(self, num_maps_manager: NumMapsManager):
        num_maps_manager.renumber()
        assert all(a.num==b for a,b in zip((x for seq in num_maps_manager.values() for x in seq.values()), itertools.count(1)))

    def test_seq_len(self, num_maps_manager: NumMapsManager, nummap_check: NumMapCheck):
        """Make sure Skip instances in SkipAttrIterMixin sequences aren't included"""
        assert  num_maps_manager.seq_len == nummap_check.skippable_len
