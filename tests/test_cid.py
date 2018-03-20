#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar` package."""

import pytest
import yaml
from pathlib import Path

@pytest.fixture
def input():
    return list(yaml.safe_load_all(Path(__file__).resolve().parents[1].joinpath("candejar/cid/ciddefs.yml").open()))

def test_yml(input):
    assert input

