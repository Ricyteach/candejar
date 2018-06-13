from candejar.mshrw.read import line_strings as read

def test_read_nodes_only():
    lines = "1\n1    1.0    2.0\n\n".split("\n")
    msh = type("Msh", (), {})()
    msh = read(msh, lines)
    assert msh.nodes == [dict(num=1, x=1.0, y=2.0)]
    assert msh.elements == []
    assert msh.boundaries == []

def test_read_elements_only():
    lines = "1\n1    1    2    0    0\n\n".split("\n")
    msh = type("Msh", (), {})()
    msh = read(msh, lines)
    assert msh.nodes == []
    assert msh.elements == [dict(num=1, i=1, j=2, k=0, l=0)]
    assert msh.boundaries == []

def test_read_boundaries_only():
    lines = "1\n1    1\n\n".split("\n")
    msh = type("Msh", (), {})()
    msh = read(msh, lines)
    assert msh.nodes == []
    assert msh.elements == []
    assert msh.boundaries == [dict(num=1, b=1)]

def test_read_nodes_elements_only():
    lines = "1\n1    1.0    2.0\n\n1\n1    1    2    0    0\n\n".split("\n")
    msh = type("Msh", (), {})()
    msh = read(msh, lines)
    assert msh.nodes == [dict(num=1, x=1.0, y=2.0)]
    assert msh.elements == [dict(num=1, i=1, j=2, k=0, l=0)]
    assert msh.boundaries == []

def test_read_elements_boundaries_only():
    lines = "1\n1    1    2    0    0\n\n1\n1    1\n\n".split("\n")
    msh = type("Msh", (), {})()
    msh = read(msh, lines)
    assert msh.nodes == []
    assert msh.elements == [dict(num=1, i=1, j=2, k=0, l=0)]
    assert msh.boundaries == [dict(num=1, b=1)]

def test_read_nodes_boundaries_only():
    lines = "1\n1    1.0    2.0\n\n1\n1    1\n\n".split("\n")
    msh = type("Msh", (), {})()
    msh = read(msh, lines)
    assert msh.nodes == [dict(num=1, x=1.0, y=2.0)]
    assert msh.elements == []
    assert msh.boundaries == [dict(num=1, b=1)]
