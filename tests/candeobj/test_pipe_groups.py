#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.PipeGroup` subclasses."""

from candejar.candeobj.pipe_groups import PipeGroup, Basic, Aluminum, Steel, Plastic, make_pipe_group

def test_PipeGroup():
    assert isinstance(PipeGroup("BASIC"), Basic)
    assert isinstance(PipeGroup("ALUMINUM"), Aluminum)
    assert isinstance(PipeGroup("STEEL"), Steel)
    assert isinstance(PipeGroup("PLASTIC"), Plastic)

def test_make_pipe_group():
    g = make_pipe_group(object(), "basic")
    assert g
