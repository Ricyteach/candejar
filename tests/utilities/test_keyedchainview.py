from typing import List

import pytest
from candejar.utilities.collections import KeyedChainView


@pytest.fixture(scope="module")
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

@pytest.mark.parametrize("s, result", [
    (slice(None),[slice(None),slice(None),slice(None),slice(None)]),
    (slice(None,None,-1), [slice(None,None,-1), slice(None,None,-1), slice(None,None,-1), slice(None,None,-1)]),
    (slice(13,23),[None, None, None, None]),
    (slice(13,-1),[None, None, None, None]),
    (slice(2,13), [slice(2, None), slice(None), slice(None), slice(None)]),
    (slice(3, 13), [None, slice(0,None), slice(None), slice(None)]),
    (slice(2, 9), [slice(2, None), slice(None), slice(None), slice(0)]),
    (slice(3, 9), [None, slice(0, None), slice(None), slice(0)]),
    (slice(2, 10), [slice(2, None), slice(None), slice(None), slice(1)]),
    (slice(3, 10), [None, slice(0, None), slice(None), slice(1)]),
    (slice(13), [slice(None), slice(None), slice(None), slice(None)]),
    (slice(None,None,2), [slice(None,None,2), slice(1,None,2), slice(0,None,2), slice(1,None,2)]),
    (slice(None,None,0), None),

])
def test_iter_seqidx_and_slice(keyed_chain_view:KeyedChainView, s:slice, result):
    seqidx_and_slice: List
    if s.step and (s.step != 1):
        with pytest.raises(NotImplementedError):
            list(keyed_chain_view._iter_seqidx_and_slice(s))
    elif s.step==0:
        with pytest.raises(ValueError):
            list(keyed_chain_view._iter_seqidx_and_slice(s))
    else:
        seqidx_and_slice = list(keyed_chain_view._iter_seqidx_and_slice(s))
        assert seqidx_and_slice == result

def test_new_keyed_chain_view(seqs):
    assert KeyedChainView(**seqs)

def test_empty_keyed_chain_view():
    c = KeyedChainView()
    assert not c
    c.append(1)
    assert c
    assert c[0] == 1

def test_non_empty_keyed_chain_view(keyed_chain_view):
    assert keyed_chain_view

@pytest.mark.parametrize("idx, value", [
    (0,1), (-1,9), (3,4), (4,5)
])
def test_index_chain_list(keyed_chain_view, idx, value):
    assert keyed_chain_view[idx] == value

@pytest.mark.parametrize("idx, value", [
    (0,99), (-1,99), (3,99), (4,99)
])
def test_insert_chain_list(keyed_chain_view, idx, value):
    old_value = keyed_chain_view[idx]
    keyed_chain_view.insert(idx, value)
    assert keyed_chain_view[idx-1 if idx<0 else idx] == value
    assert keyed_chain_view[idx if idx<0 else idx+1] == old_value

@pytest.mark.parametrize("idx", [
    12, -13, 28
])
def test_index_chain_list(keyed_chain_view, idx):
    with pytest.raises(IndexError):
        keyed_chain_view[idx]
    with pytest.raises(IndexError):
        del keyed_chain_view[idx]

def test_len_chain_list(keyed_chain_view):
    assert len(keyed_chain_view)==12

