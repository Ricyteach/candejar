#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cid.cidline` module."""

import pytest
from candejar.cid.cidline import make_cid_line_cls
from dataclasses import astuple

yml_sample = [
    "OBJ",
    dict(
        A1=dict(
            prefix='A-1',
            # ANALYS or DESIGN
            mode=(8, 'ANALYS'),
            # 1, 2, or 3
            level=(2, 3),
            method=(2, 1),
            ngroups=(3, 1),
            heading=(60, 'CID file from canderw: Rick Teachey, rick@teachey.org'),
            iterations=(5, -99),
            culvertid=(5, 0, True),
            processid=(5, 0, True),
            subdomainid=(5, 0, True)
        ),
        D1=dict(
            prefix= "D-1",
            # Note: moved limit field to line prefix
            # Limit: [1, " "]
            id= [4, 0],
            # 1: Isotropic, 2: Orthotropic,
            # 3: Duncan/Selig, 4: Overburden,
            # 5: Extended Hardin, 6: Interface,
            # 7: Composite Link, 8: Mohr/Coulomb
            model= [5, 1],
            density= [10, 0.0],
            name= [20, ""],
            # overburden model only
            layers= [2, 0, True]
        ),
        E1=dict(
            prefix='E-1',
            start=(5, 0),
            last=(5, 0),
            factor=(10, 1.0),
            comment=(40, '')
        )
    )
]

lines = [
    "                      A-1!!ANALYS   3 1  1CID file from canderw: Rick Teachey, rick@teachey.org         -99               ",
    "                      D-1!!    0    1      0.00                      ",
    "                      E-1!!    1   40      1.25Factor for load step #1                 "
    ]

data = [
    ("ANALYS", 3, 1, 1, "CID file from canderw: Rick Teachey, rick@teachey.org", -99, 0, 0, 0),
    (0, 1, 0.0, "", 0),
    (1, 40, 1.25, "Factor for load step #1")
    ]

_, line_defs_dict = yml_sample
line_classes = [make_cid_line_cls(name, **dfntn_dict) for name, dfntn_dict in line_defs_dict.items()]

@pytest.fixture(params=zip(line_classes, data, lines),ids=[cls.__name__ for cls in line_classes])
def class_data_and_line(request):
    """A 3 tuple of class, data, and line that go together.
    """
    return request.param

class TestCidLine:
    def test_parse(self, class_data_and_line):
        """Confirm CideLine child classes read lines correctly."""
        cls, data, line = class_data_and_line
        assert astuple(cls.parse(line)) == data
    def test_format(self, class_data_and_line):
        """Confirm CideLine child classes write data correctly."""
        cls, data, line = class_data_and_line
        assert format(cls(*data), "cid") == line
