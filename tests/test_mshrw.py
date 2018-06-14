from candejar.mshrw.read import line_strings as read

def test_read_all(msh_all_obj):
    msh = msh_all_obj
    assert msh.nodes == [dict(num=1, x=1.0, y=2.0)]
    assert msh.elements == [dict(num=1, i=1, j=2, k=0, l=0)]
    assert msh.boundaries == [dict(num=1, b=1)]

def test_read_nodes_only(msh_nodes_obj):
    msh = msh_nodes_obj
    assert msh.nodes == [dict(num=1, x=1.0, y=2.0)]
    assert msh.elements == []
    assert msh.boundaries == []

def test_read_elements_only(msh_elements_obj):
    msh = msh_elements_obj
    assert msh.nodes == []
    assert msh.elements == [dict(num=1, i=1, j=2, k=0, l=0)]
    assert msh.boundaries == []

def test_read_boundaries_only(msh_boundaries_obj):
    msh = msh_boundaries_obj
    assert msh.nodes == []
    assert msh.elements == []
    assert msh.boundaries == [dict(num=1, b=1)]

def test_read_nodes_elements_only(msh_nodes_elements_obj):
    msh = msh_nodes_elements_obj
    assert msh.nodes == [dict(num=1, x=1.0, y=2.0)]
    assert msh.elements == [dict(num=1, i=1, j=2, k=0, l=0)]
    assert msh.boundaries == []

def test_read_elements_boundaries_only(msh_elements_boundaries_obj):
    msh = msh_elements_boundaries_obj
    assert msh.nodes == []
    assert msh.elements == [dict(num=1, i=1, j=2, k=0, l=0)]
    assert msh.boundaries == [dict(num=1, b=1)]

def test_read_nodes_boundaries_only(msh_nodes_boundaries_obj):
    msh = msh_nodes_boundaries_obj
    assert msh.nodes == [dict(num=1, x=1.0, y=2.0)]
    assert msh.elements == []
    assert msh.boundaries == [dict(num=1, b=1)]
