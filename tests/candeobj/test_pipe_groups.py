#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.PipeGroupComponent` subclasses."""

import pytest

from candejar.candeobj.pipe_groups import PipeGroup, Basic, Aluminum, Steel, Plastic, make_pipe_group, CandeValueError
from candejar.candeobj.bases import CandeNum, CandeStr

@pytest.fixture
def dumb_cid():
    cid = type("DumbCid",(),{})()
    cid.pipe_groups = []
    return cid

@pytest.fixture
def analysis_asd_cid(dumb_cid):
    dumb_cid.mode = "ANALYS"
    dumb_cid.method = 0
    return dumb_cid

@pytest.mark.parametrize("name,Cls", [
    ("Basic", Basic),
    ("Aluminum", Aluminum),
    ("Steel", Steel),
    ("Plastic", Plastic),
])
def test_PipeGroup(name, Cls):
    assert isinstance(PipeGroup(CandeStr(name)), Cls)

@pytest.mark.parametrize("name,Cls,kwargs", [
    ("Basic", Basic, {}),
    # TODO: test Aluminum after implementation
    # ("Aluminum", Aluminum, {}),
    # TODO: test Steel after implementation
    # ("Steel", Steel, {}),
    ("Plastic", Plastic, dict(walltype="GENERAL")),
])
def test_make_pipe_group(name, Cls, analysis_asd_cid, kwargs):
    g = make_pipe_group(analysis_asd_cid, type_=CandeStr(name), num=CandeNum(10), **kwargs)
    assert isinstance(g, Cls)

def test_plastic_missing_walltype(analysis_asd_cid):
    with pytest.raises(CandeValueError):
        make_pipe_group(analysis_asd_cid, type_=CandeStr("Plastic"))
