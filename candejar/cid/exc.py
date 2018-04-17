# -*- coding: utf-8 -*-

"""`cid` module exceptions"""

class CIDError(Exception):
    """Base exception for `cid` module"""
    pass

class LineError(CIDError):
    pass

class LineParseError(LineError):
    """Raised when a cid line type parser cannot successfully parse an input string."""
    pass
