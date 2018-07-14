# -*- coding: utf-8 -*-

"""`candeobj` module exceptions"""

class CandeError(Exception):
    pass

class CandeValueError(CandeError, ValueError):
    pass

class CandeAttributeError(CandeError, AttributeError):
    pass

class CandeTypeError(CandeError, TypeError):
    pass

class CandeKeyError(CandeError, KeyError):
    pass
