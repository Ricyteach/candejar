#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj` module."""

from candejar import msh
from candejar.candeobj import Node
from candejar.candeobj.candeobj import CandeObj
from candejar.candeobj.connections import MergedConnection
from candejar.candeobj.nummap import NumMapsManager
from candejar.cidobjrw.names import SEQ_LINE_TYPE_TOTALS
from candejar.msh import Msh
from candejar.utilities import skip


def test_candebase():
    cande_obj = CandeObj()
    assert cande_obj
    assert not cande_obj.nodes
    assert not cande_obj.elements
    assert not cande_obj.boundaries


def test_load_blank_cidobj(cid_blank):
    cande_obj = CandeObj.load_cidobj(cid_blank)
    assert cande_obj
    assert not cande_obj.nodes
    assert not cande_obj.elements
    assert not cande_obj.boundaries


def test_load_cid_standard(cid_obj_standard, cande_obj_standard):
    assert all(getattr(cande_obj_standard, name) == getattr(cid_obj_standard, name) for name in SEQ_LINE_TYPE_TOTALS)
    assert cande_obj_standard.nodes
    assert cande_obj_standard.elements
    assert cande_obj_standard.boundaries
    assert cande_obj_standard.nodes["section1"]
    assert cande_obj_standard.elements["section1"].nodes
    assert cande_obj_standard.boundaries["section1"].nodes


def test_add_from_msh_all_obj(monkeypatch, cande_obj_standard: CandeObj, msh_all_obj: Msh):
    def mock_open(*args, **kwargs):
        return msh_all_obj
    monkeypatch.setattr(msh, "open", mock_open)
    file_name = "FAKE"
    cande_obj_standard.add_from_msh(file_name)
    assert cande_obj_standard.nodes
    assert cande_obj_standard.elements
    assert cande_obj_standard.boundaries
    assert cande_obj_standard.nodes["section1"]
    assert cande_obj_standard.elements["section1"].nodes
    assert cande_obj_standard.boundaries["section1"].nodes
    assert cande_obj_standard.nodes["section2"]
    assert cande_obj_standard.elements["section2"].nodes
    assert cande_obj_standard.boundaries["section2"].nodes


def test_update_totals(new_c_obj):
    n_attrs = "ngroups nsteps nnodes nelements".split()
    assert all(getattr(new_c_obj, attr) == v for attr, v in zip(n_attrs, (0, 0, 0, 0)))
    new_c_obj.elements["TEST"] = []
    new_c_obj.elements.append(dict(num=1, i=1, j=2, k=0, l=0, mat=1, step=1))
    new_c_obj.update_totals()
    assert all(getattr(new_c_obj, attr) == v for attr, v in zip(n_attrs, (1, 1, 2, 1)))


def test_make_connections(new_c_obj):
    new_c_obj.nodes["section1"] = []
    new_c_obj.nodes.append(Node(num=1,x=0,y=0))
    new_c_obj.nodes.append(Node(num=2,x=0,y=0))
    nodes = (new_c_obj.nodes[i] for i in range(2))
    new_c_obj.connections.append(MergedConnection(items=[*nodes]))
    new_c_obj.make_connections()
    # First node is master
    assert new_c_obj.nodes[0].master is None
    # Second node is slave
    assert new_c_obj.nodes[1].master.num==1


def test_globalize_node_nums(new_c_obj):
    A1 = Node(num=2000, x=1, y=1)
    B1 = Node(num=2001, x=2, y=2)
    A2 = Node(num=2000, x=1, y=1)
    B2 = Node(num=2001, x=2, y=2)
    new_c_obj.nodes["Section1"] = [A1, B1]
    new_c_obj.nodes["Section2"] = [A2, B2]
    node_convert_map = NumMapsManager(new_c_obj.nodes)
    node_convert_map.renumber()
    A2.num = skip.SkipInt(A2.num)
    B2.num = skip.SkipInt(B2.num)
    new_c_obj.globalize_node_nums(node_convert_map)
    assert A1.num == 1
    assert B1.num == 2
    assert A2.num == 2000
    assert B2.num == 2001
