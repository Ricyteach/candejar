#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cidobjrw.cidrwabc` module."""
import pytest

from candejar.cidobjrw.cidrwabc import CidRW
from candejar.cidobjrw.exc import CidRWSubclassSignatureError

def test_subclass():
    class Child(CidRW):
        def process_line_strings(self):
            while True:
                yield
    assert Child()

def test_subclass_fail_on_no_default_arguments():
    with pytest.raises(CidRWSubclassSignatureError):
        class _(CidRW):
            def __init__(self, _): ...
            def process_line_strings(self): ...

def test_subclass_fail_on_no_process_line_strings_method():
    with pytest.raises(TypeError):
        class Child(CidRW):
            pass
        Child()

def test_from_lines(cidmock, cidmock_lines, cidmock_types):
    class Mocked(CidRW):
        def __init__(self):
            self.__dict__ = cidmock.__dict__
        def process_line_strings(self):
            while True:
                yield
        def process_line_types(self):
            yield from iter(cidmock_types)
    mock = Mocked.from_lines(cidmock_lines)
    assert mock
