#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.nummap` module."""
from typing import Dict

import pytest
from dataclasses import make_dataclass
from types import SimpleNamespace as SimpleNs

from candejar.candeobj.nummap import NumMap, NumMapsManager


Has_num = make_dataclass("Has_num", [("num", int),])
NoNum = make_dataclass("NoNum", [])
Has_seq_map = make_dataclass("Has_seq_map", [("seq_map", Dict),])


has_n_params_list = [SimpleNs(list = [Has_num(i) for i in range(3)], len=3),
                                        ]


@pytest.fixture(params=has_n_params_list)
def has_n_test(request):
    return request.param


@pytest.fixture
def num_map(has_n_test):
    return NumMap(has_n_test.list)


class TestNumMap:
    def test_no_num_attribute(self, num_map):
        with pytest.raises(AttributeError):
            NumMap([NoNum()])

    def test_falsey(self, num_map):
        assert not NumMap([])

    def test_truthy(self, num_map):
        assert num_map

    def test_len(self, num_map, has_n_test):
        assert len(num_map) == has_n_test.len


@pytest.fixture
def has_n_map(has_n_test):
    return Has_seq_map(seq_map=dict(x=has_n_test.list))


@pytest.fixture
def no_n_map():
    return Has_seq_map(seq_map=dict(x=[NoNum()]))


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
