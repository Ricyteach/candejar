#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.PipeGroupComponent` subclasses."""

import pytest

from candejar.candeobj.pipe_groups import PipeGroup, Basic, Aluminum, Steel, Plastic, make_pipe_group
from candejar.candeobj.bases import CandeNum, CandeStr


@pytest.mark.parametrize("name,Cls", [
    ("Basic", Basic),
    ("Aluminum", Aluminum),
    ("Steel", Steel),
    ("Plastic", Plastic),
])
def test_PipeGroup(name, Cls):
    assert isinstance(PipeGroup(CandeStr(name), CandeNum(0)), Cls)

def test_make_pipe_group():
    cid = type("C",(),{})()
    cid.pipe_groups = []
    cid.mode = "ANALYS"
    g = make_pipe_group(cid, "basic")
    assert g
