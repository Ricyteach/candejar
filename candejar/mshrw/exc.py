# -*- coding: utf-8 -*-

"""`mshrw` module exceptions"""


class MSHRWError(Exception):
    """Base exception for `mshrw` module"""
    pass


class MSHLineProcessingError(MSHRWError):
    """Raised when error occurs during processing."""
    total: int  # total items in the section where error occurred
    line: str  # the line that caused the error
