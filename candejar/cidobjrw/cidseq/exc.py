# -*- coding: utf-8 -*-

"""`cidobjrw.cidseq` module exceptions"""

from ..exc import CIDObjError

class CidSeqError(CIDObjError):
    pass

class CIDSubSeqIndexError(CidSeqError, IndexError):
    pass

class CheckCompleteNotSet(CidSeqError):
    pass
