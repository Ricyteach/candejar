# -*- coding: utf-8 -*-

"""`cidrw` module exceptions"""

class CIDRWError(Exception):
    """Base exception for `cidrw` module"""
    pass


class IncompleteCIDLinesError(CIDRWError):
    """Raised when STOP statement not reached during processing."""
    pass


class CIDLineProcessingError(CIDRWError):
    """Raised when error occurs during processing."""
    pass
