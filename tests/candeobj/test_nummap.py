#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.nummap` module."""

import pytest
from dataclasses import make_dataclass

from candejar.candeobj.nummap import NumMap


@pytest.fixture
def HasNum():
    return make_dataclass("HasNum", [("num", int),])


@pytest.fixture
def NoNum():
    return make_dataclass("NoNum", [])


@pytest.fixture
def has_n_list(HasNum):
    return [HasNum(i) for i in range(3)]


@pytest.fixture
def num_map(has_n_list):
    return NumMap(has_n_list)


def test_num_map(num_map, NoNum):
    with pytest.raises(AttributeError):
        NumMap([NoNum()])
    assert not NumMap([])
    assert num_map
