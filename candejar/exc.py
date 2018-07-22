# -*- coding: utf-8 -*-

"""`candejar` exceptions"""


class CandejarError(Exception):
    pass


class CandejarTypeError(CandejarError, TypeError):
    pass


class CandejarValueError(CandejarError, ValueError):
    pass


class CandeAttributeError(CandejarError, AttributeError):
    pass
