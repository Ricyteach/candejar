# -*- coding: utf-8 -*-

"""`mshrw` module exceptions"""


class MSHRWError(Exception):
    """Base exception for `mshrw` module"""
    pass


class MSHLineProcessingError(MSHRWError):
    """Raised when error occurs during processing."""
    pass
