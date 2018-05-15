# -*- coding: utf-8 -*-

"""Special tools for working with mapping types."""

import keyword, builtins

def isvalid(ident: str) -> bool:
    """Determines if string is valid Python identifier."""
    flag = True

    if not isinstance(ident, str):
        raise TypeError("expected str, but got {!r}".format(type(ident)))

    if not ident.isidentifier():
        flag = False

    if keyword.iskeyword(ident):
        flag = False

    if ident in dir(builtins):
        flag = False

    return flag
