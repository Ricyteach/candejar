# -*- coding: utf-8 -*-

"""`candeobj` module exceptions"""

class CandeError(Exception):
    pass

class CandeValueError(CandeError, ValueError):
    pass
