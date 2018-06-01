from typing import List

import pytest
from candejar.utilities.collections import ChainSequence, SpecialValueError


@pytest.fixture
def seqs():
    return [1,2,3], [4,5,6], [7,8,9], [10,11,12]

@pytest.fixture
def chain_seq(seqs):
    return ChainSequence(*seqs)

@pytest.mark.parametrize("i, result", [
    (-1, None),
    (0, [0, None, None, None]),
    (1, [1, None, None, None]),
    (2, [2, None, None, None]),
    (3, [None, 0, None, None]),
    (4, [None, 1, None, None]),
    (5, [None, 2, None, None]),
    (6, [None, None, 0, None]),
    (7, [None, None, 1, None]),
    (8, [None, None, 2, None]),
    (9, [None, None, None, 0]),
    (10, [None, None, None, 1]),
    (11, [None, None, None, 2]),
    (12, [None, None, None, None]),
])
def test_iter_seqidx_and_idx(chain_seq, i, result):
    if i<0:
        with pytest.raises(SpecialValueError):
            list(chain_seq._iter_seqidx_and_idx(i))
    else:
        assert list(chain_seq._iter_seqidx_and_idx(i)) == result

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
def test_iter_seqidx_and_slice(chain_seq:ChainSequence, s:slice, result):
    seqidx_and_slice: List
    if s.step and (s.step != 1):
        with pytest.raises(NotImplementedError):
            list(chain_seq._iter_seqidx_and_slice(s))
    elif s.step==0:
        with pytest.raises(ValueError):
            list(chain_seq._iter_seqidx_and_slice(s))
    else:
        seqidx_and_slice = list(chain_seq._iter_seqidx_and_slice(s))
        assert seqidx_and_slice == result

def test_new_chain_seq(seqs):
    assert ChainSequence(*seqs)

def test_empty_chain_seq():
    c = ChainSequence()
    assert not c
    c.append(1)
    assert c
    assert c[0] == 1

def test_non_empty_chain_seq(chain_seq):
    assert chain_seq

@pytest.mark.parametrize("idx, value", [
    (0,1), (-1,9), (3,4), (4,5)
])
def test_index_chain_list(chain_seq, idx, value):
    assert chain_seq[idx] == value

@pytest.mark.parametrize("idx, value", [
    (0,99), (-1,99), (3,99), (4,99)
])
def test_insert_chain_list(chain_seq, idx, value):
    old_value = chain_seq[idx]
    chain_seq.insert(idx, value)
    assert chain_seq[idx-1 if idx<0 else idx] == value
    assert chain_seq[idx if idx<0 else idx+1] == old_value

@pytest.mark.parametrize("idx", [
    12, -13, 28
])
def test_index_chain_list(chain_seq, idx):
    with pytest.raises(IndexError):
        chain_seq[idx]
    with pytest.raises(IndexError):
        del chain_seq[idx]

def test_len_chain_list(chain_seq):
    assert len(chain_seq)==12

