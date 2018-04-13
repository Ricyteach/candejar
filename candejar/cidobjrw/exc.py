# -*- coding: utf-8 -*-

"""`cidobjrw` module exceptions"""

class CIDObjError(Exception):
    """Base exception for `cidobjrw` module"""
    pass

class InvalidCIDLinesError(CIDObjError):
    """Raised when `StopIteration` encountered unexpectedly during cid line processing."""
    pass

class IncompleteCIDLinesError(InvalidCIDLinesError):
    """Raised when cid line file appears to be incomplete."""
    pass

