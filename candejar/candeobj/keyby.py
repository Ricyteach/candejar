# -*- coding: utf-8 -*-

"""Functions to create keys for looking up the dynamic cande object types."""

from typing import Callable, Tuple

from ..cid import CidLineType


def key_by_cid_linetype(top_cls) -> Callable[[type], Tuple[CidLineType]]:
    # return ChildRegistryMixin._make_reg_key(pipe_cls)
    def make_key(sub_cls) -> Tuple[CidLineType]:
        sub_class_linetypes = (c.line_type for c in sub_cls.mro() if issubclass(c, top_cls))
        key = tuple(reversed(list(sub_class_linetypes)))
        return key
    return make_key
