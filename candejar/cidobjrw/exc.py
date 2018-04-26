# -*- coding: utf-8 -*-

"""`cidobjrw` module exceptions"""

class CIDObjError(Exception):
    """Base exception for `cidobjrw` module"""
    pass

class CidRWSubclassSignatureError(CIDObjError):
    """Raised when CidRW sublcassed with required init arguments"""
    pass

class CidObjFromLinesError(CIDObjError):
    """Raised when a problem occurs during object construction for .cid file lines input"""
    pass
