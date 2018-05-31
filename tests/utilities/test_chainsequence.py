import pytest
from candejar.utilities.collections import ChainSequence

@pytest.fixture
def seqs():
    return [1,2,3], [4,5,6], [7,8,9]

@pytest.fixture
def chain_seq(seqs):
    return ChainSequence(*seqs)

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
    9, -10, 25
])
def test_index_chain_list(chain_seq, idx):
    with pytest.raises(IndexError):
        chain_seq[idx]
    with pytest.raises(IndexError):
        del chain_seq[idx]

def test_len_chain_list(chain_seq):
    assert len(chain_seq)==9
