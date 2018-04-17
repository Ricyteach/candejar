# -*- coding: utf-8 -*-

"""`cidprocessing` module exceptions"""

class CIDProcessingError(Exception):
    """Base exception for `cidprocessing` module"""
    pass

class CIDProcessingIndexError(CIDProcessingError, IndexError):
    """Raised when an invalid member number for a cid sub sequence has been requested."""
    pass
