#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Fixtures for use across the candeobj testing suite"""

import pytest
from typing import Dict, NamedTuple, List
from dataclasses import make_dataclass
from candejar.utilities.skip import SkipAttrIterMixin

from candejar.candeobj.candeobj import CandeObj


@pytest.fixture
def cande_obj_standard(cid_obj_standard):
    cobj = CandeObj.load_cidobj(cid_obj_standard)
    return cobj


@pytest.fixture
def new_c_obj():
    c = CandeObj()
    return c


@pytest.fixture(scope="session")
def SkipNumList():
    class SkipNumList(SkipAttrIterMixin, List):
        """Object with skippable num attributes"""
        skippable_attr = "num"
    return SkipNumList


@pytest.fixture(scope="session")
def No_num():
    return make_dataclass("No_num", [])


@pytest.fixture(scope="session")
def Has_num():
    return make_dataclass("Has_num", [("num", int),])


@pytest.fixture(scope="session")
def Has_seq_map(Has_num):
    return make_dataclass("Has_seq_map", [("seq_map", Dict[str, List[Has_num]]),])


@pytest.fixture(scope="session")
def NumMapCheck():
    class NumMapCheck(NamedTuple):
        """Each instance is a check"""
        length: int
        iter_len: int
        skippable_len: int
        bad_key: int
        has_nums: List
    return NumMapCheck


