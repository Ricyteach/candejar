# -*- coding: utf-8 -*-

"""`cidobjrw` module exceptions"""

class CIDObjError(Exception):
    """Base exception for `cidobjrw` module"""
    pass

class IncompleteCIDLinesError(CIDObjError):
    """Raised when STOP statement not reached during processing."""
    pass

class CIDLineProcessingError(CIDObjError):
    """Raised when error occurs during processing."""
    pass

class CidRWSubclassSignatureError(CIDObjError):
    """Raised when CidRW sublcassed with required init arguments"""
    pass
