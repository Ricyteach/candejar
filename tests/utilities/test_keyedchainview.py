import pytest
from candejar.utilities.collections import KeyedChainView


@pytest.fixture
def seqs():
    x_list = [1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]
    names = "ABCD"
    return dict(zip(names, x_list))

@pytest.fixture
def keyed_chain_view(seqs):
    return KeyedChainView(**seqs)

@pytest.mark.parametrize("i, result", [
    (-1, 12),
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (8, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (12, None),
])
def test_get_seq_idx(keyed_chain_view, i, result):
    if result is None:
        with pytest.raises(IndexError):
            keyed_chain_view.get_seq_idx(i)
    else:
        s, i = keyed_chain_view.get_seq_idx(i)
        assert s[i] == result

def test_unpack(keyed_chain_view):
    assert [*keyed_chain_view]

def test_keyed_chain_view(seqs):
    assert KeyedChainView(**seqs)

def test_new_keyed_chain_view():
    c = KeyedChainView()
    assert not c
    c.seq_map["A"] = []
    assert not c
    c.append(1)
    assert c
    assert c[0] == 1

@pytest.mark.parametrize("idx, value", [
    (0,99), (-1,99), (3,99), (4,99)
])
def test_insert_chain_list(keyed_chain_view, idx, value):
    old_value = keyed_chain_view[idx]
    keyed_chain_view.insert(idx, value)
    assert keyed_chain_view[idx-1 if idx<0 else idx] == value
    assert keyed_chain_view[idx if idx<0 else idx+1] == old_value

@pytest.mark.parametrize("i, result", [
    (-1, 12),
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (8, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (12, None),
])
def test_index_chain_list(keyed_chain_view: KeyedChainView, i, result):
    if result is None:
        with pytest.raises(IndexError):
            keyed_chain_view[i]
        with pytest.raises(IndexError):
            keyed_chain_view[i] = None
        with pytest.raises(IndexError):
            del keyed_chain_view[i]
    else:
        assert keyed_chain_view[i] == result
        keyed_chain_view[i] = None
        assert keyed_chain_view[i] == None
        del keyed_chain_view[i]
        assert len(keyed_chain_view) == 11
        keyed_chain_view.insert(1, None)
        assert len(keyed_chain_view) == 12
        assert keyed_chain_view.pop(1) == None
        assert len(keyed_chain_view) == 11

def test_len_chain_list(keyed_chain_view):
    assert len(keyed_chain_view)==12


