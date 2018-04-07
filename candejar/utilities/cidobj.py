# -*- coding: utf-8 -*-

"""Special tools for working with cidobj types."""

from typing import Any, Optional, Callable


class SpecialError(Exception):
    pass


def forgiving_dynamic_attr(obj: Any, attr_getter: Callable[[], Optional[str]]) -> Any:
    """Retrieves an attribute name determined by the attribute getter.

    obj: the object whose attribute will be returned, or itself will be returned
    attr_getter: a function accepting no arguments that returns either None or
    the attr name. if the result is not a string, the obj is returned by the function.
    """
    target_obj_name = attr_getter()
    try:
        return getattr(obj, target_obj_name)
    except TypeError:
        return obj
    except AttributeError as e:
        raise SpecialError("The attr_getter did not produce an available attr name") from e
