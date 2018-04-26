#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidprocessing` module."""
import pytest
from types import SimpleNamespace
from candejar.cidprocessing.main import process

def process_(cid):
    for result in process(cid):
        yield result.__name__

def test_processing(cidmock):
    names = " ".join(process_(cidmock))
    assert names[:5] == "A1 A2"
    print(f"\n{names}")
