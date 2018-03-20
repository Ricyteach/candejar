#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.cid.cidline` module."""
import pytest
from candejar.cid.cidline import make_cid_line_cls

yml_sample = [
    "OBJ",
    dict(
        A1=dict(
            prefix='A-1',
            # ANALYS or DESIGN
            Mode=(8, 'ANALYS'),
            # 1, 2, or 3
            Level=(2, 3),
            Method=(2, 1),
            NGroups=(3, 1),
            Heading=(60, 'CID file from canderw: Rick Teachey, rick@teachey.org'),
            Iterations=(5, -99),
            CulvertID=(5, 0, True),
            ProcessID=(5, 0, True),
            SubdomainID=(5, 0, True)
        ),
        E1=dict(
            prefix='E-1',
            Start=(5, 0),
            Last=(5, 0),
            Factor=(10, 1.0),
            Comment=(60, '')
        )
    )
]

lines = [
    "                      A-1!!ANALYS   3 1  1CID file from canderw: Rick Teachey, rick@teachey.org         =99    0    0    0",
    "                      E-1!!    1   40      1.25Factor for load step #1                                     "
]
data = [
    ("ANALYS", 3, 1, 1, "CID file from canderw: Rick Teachey, rick@teachey.org", -99, 0, 0, 0),
    (1, 40, 1.25, "Factor for load step #1")
]


@pytest.fixture
def line_classes():
    """CidLine classes.
    """
    _, line_defs_dict = yml_sample
    return [make_cid_line_cls(name, **dfntn_dict) for name, dfntn_dict in line_defs_dict.items()]

@pytest.fixture
def class_data_and_line_sets(line_classes):
    """A 3 tuple of class, data, and line that go together.
    """
    return list(zip(line_classes, lines, data))

@pytest.fixture(params = class_data_and_line_sets, ids = yml_sample[1])
def class_data_and_line(request):
    return request.param

class TestCidLine:
    def test_parse(self, class_data_and_line):
        """Confirm CideLine child classes read lines correctly."""
        assert False
    def test_format(self, class_data_and_line):
        """Confirm CideLine child classes write data correctly."""
        assert False
