#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cid.cidfield` module."""

import pytest
import yaml
from pathlib import Path
from candejar.cid.cidfield import Field, Align

# cidfield tests

@pytest.fixture
def input():
    return list(yaml.safe_load_all(Path(__file__).resolve().parents[1].joinpath("candejar/cid/ciddefs.yml").open()))

def test_yml(input):
    assert input

#Objects used in Field testing
field_objs = {  "int=1 width=1": Field(1, 1),
                "int=1 width=2": Field(2, 1),
                "int=1 width=1 optional": Field(1, 1, optional=True),
                "int=1 width=2 align=left": Field(2, 1, align=Align.LEFT),
                "float=1.0 width=10": Field(10, 1.0),
                "float=1.0 width=10 optional": Field(10, 1.0, optional=True),
                "float=1.0 width=10 precision=1": Field(10, 1.0, precision=1)
                }

@pytest.fixture(params = list(field_objs), ids = list(field_objs))
def field_test_name(request):
    return request.param


class TestField:
    parse_data = {  "int=1 width=1": [("2", 2), ("1", 1)],
                    "int=1 width=1 optional": [(" ", 1), (None, 1)],
                    "int=1 width=2": [(" 2", 2), (" 1", 1)],
                    "int=1 width=2 align=left": [("2 ", 2), ("1 ", 1)],
                    "float=1.0 width=10": [(" 1.0000000", 1.0), (" 2.0000000", 2.0)],
                    "float=1.0 width=10 optional": [("          ", 1.0), (None, 1.0)],
                    "float=1.0 width=10 precision=1": [(" 1.0000000", 1.0), (" 2.0000000", 2.0)]
                    }
    def test_parse(self, field_test_name):
        for input,result in self.parse_data[field_test_name]:
            assert field_objs[field_test_name].parse(input) == result

    spec_data = {   "int=1 width=1": " >1d",
                    "int=1 width=1 optional": " >1d",
                    "int=1 width=2": " >2d",
                    "int=1 width=2 align=left": " <2d",
                    "float=1.0 width=10": " >10.2f",
                    "float=1.0 width=10 optional": " >10.2f",
                    "float=1.0 width=10 precision=1": " >10.1f"
                    }
    def test_spec(self, field_test_name):
        result = self.spec_data[field_test_name]
        obj = field_objs[field_test_name]
        assert result == obj.spec

    bspec_data = {  "int=1 width=1": " >1",
                    "int=1 width=1 optional": " >1",
                    "int=1 width=2": " >2",
                    "int=1 width=2 align=left": " <2",
                    "float=1.0 width=10": " >10",
                    "float=1.0 width=10 optional": " >10",
                    "float=1.0 width=10 precision=1": " >10"
                    }
    def test_bspec(self, field_test_name):
        result = self.bspec_data[field_test_name]
        assert field_objs[field_test_name].blank_spec == result

    regex_data = {  "int=1 width=1": ("Name", "(?P<Name>.{1})"),
                    "int=1 width=1 optional": ("Name", "(?P<Name>.{1})?"),
                    "int=1 width=2": ("Name", "(?P<Name>.{2})"),
                    "int=1 width=2 align=left": ("Name", "(?P<Name>.{2})"),
                    "float=1.0 width=10": ("Name", "(?P<Name>.{10})"),
                    "float=1.0 width=10 optional": ("Name", "(?P<Name>.{10})?"),
                    "float=1.0 width=10 precision=1": ("Name", "(?P<Name>.{10})")
                    }
    def test_regex(self, field_test_name):
        input, result = self.regex_data[field_test_name]
        assert field_objs[field_test_name].regex(input) == result

    format_data = { "int=1 width=1": [(1, "1")],
                    "int=1 width=1 optional": [(None, " ")],
                    "int=1 width=2": [(1, " 1")],
                    "int=1 width=2 align=left": [(1, "1 ")],
                    "float=1.0 width=10": [(1.0, "      1.00"), (2.0, "      2.00")],
                    "float=1.0 width=10 optional": [(None, "          ")],
                    "float=1.0 width=10 precision=1": [(1.0, "       1.0"), (2.0, "       2.0")]
                    }
    def test_format(self, field_test_name):
        for input,result in self.format_data[field_test_name]:
            assert field_objs[field_test_name].format(input) == result

    precision_data = {  "int=1 width=1": None,
                        "int=1 width=1 optional": None,
                        "int=1 width=2": None,
                        "int=1 width=2 align=left": None,
                        "float=1.0 width=10": 2,
                        "float=1.0 width=10 optional": 2,
                        "float=1.0 width=10 precision=1": 1
                        }
    def test_precision(self, field_test_name):
        result = self.precision_data[field_test_name]
        assert field_objs[field_test_name].precision == result

    align_data = {  "int=1 width=1": ">",
                    "int=1 width=1 optional": ">",
                    "int=1 width=2": ">",
                    "int=1 width=2 align=left": "<",
                    "float=1.0 width=10": ">",
                    "float=1.0 width=10 optional": ">",
                    "float=1.0 width=10 precision=1": ">"
                    }
    def test_align(self, field_test_name):
        result = self.align_data[field_test_name]
        assert field_objs[field_test_name].align == result

    default_data = { "int=1 width=1": 1,
                     "int=1 width=1 optional": 1,
                     "int=1 width=2": 1,
                     "int=1 width=2 align=left": 1,
                     "float=1.0 width=10": 1.0,
                     "float=1.0 width=10 optional": 1.0,
                     "float=1.0 width=10 precision=1": 1.0
                    }
    def test_default(self, field_test_name):
        result = self.default_data[field_test_name]
        assert field_objs[field_test_name].default == result

    width_data = {  "int=1 width=1": 1,
                    "int=1 width=1 optional": 1,
                    "int=1 width=2": 2,
                    "int=1 width=2 align=left": 2,
                    "float=1.0 width=10": 10,
                    "float=1.0 width=10 optional": 10,
                    "float=1.0 width=10 precision=1": 10
                    }
    def test_width(self, field_test_name):
        result = self.width_data[field_test_name]
        assert field_objs[field_test_name].width == result

    type_data = {   "int=1 width=1": "d",
                    "int=1 width=1 optional": "d",
                    "int=1 width=2": "d",
                    "int=1 width=2 align=left": "d",
                    "float=1.0 width=10": "f",
                    "float=1.0 width=10 optional": "f",
                    "float=1.0 width=10 precision=1": "f"
                    }
    def test_type(self, field_test_name):
        result = self.type_data[field_test_name]
        assert field_objs[field_test_name].type_ == result
