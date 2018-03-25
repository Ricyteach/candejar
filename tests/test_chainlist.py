import pytest
from candejar.utilities.chainlist import ChainSequences

@pytest.fixture
def seqs():
    return [1,2,3], [4,5,6], [7,8,9]

@pytest.fixture
def chain_seq(seqs):
    return ChainSequences(*seqs)

def test_empty_chain_seq():
    assert not ChainSequences()

def test_non_empty_chain_seq(chain_seq):
    assert chain_seq

@pytest.mark.parametrize("idx, value", [
    (0,1), (-1,9), (3,4), (4,5)
])
def test_index_chain_list(chain_seq, idx, value):
    assert chain_seq[idx] == value

@pytest.mark.parametrize("idx", [
    9, -10, 25
])
def test_index_chain_list(chain_seq, idx):
    with pytest.raises(IndexError):
        chain_seq[idx]
