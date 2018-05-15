# -*- coding: utf-8 -*-

"""Dynamically loads CID line classes from `ciddefs.yml`."""

from types import SimpleNamespace
from typing import Any, List

from ..utilities.loadyml import load_yml_objs
from .cidline import make_cid_line_cls

def make_cid_line_classes() -> SimpleNamespace:
    line_cls_groups = {name:dct for name,dct in load_yml_objs()}
    line_cls_namespaces = SimpleNamespace(**{name:SimpleNamespace(**{clsname:make_cid_line_cls(clsname, **definitions)
                                                                     for clsname,definitions in line_cls_def.items()})
                                             for name,line_cls_def in line_cls_groups.items()})
    return line_cls_namespaces

cidlineclassgroups = make_cid_line_classes()

cidlineclasses = SimpleNamespace(**{k:v for group in vars(cidlineclassgroups).values() for k,v in vars(group).items()})

def __getattr__(name: str) -> Any:
    try:
        return getattr(cidlineclassgroups, name)
    except AttributeError:
        pass
    try:
        return getattr(cidlineclasses, name)
    except AttributeError:
        pass
    raise AttributeError(f"module 'cidlineclasses' has no attribute {name}")

def __dir__() -> List[str]:
    return list(vars(cidlineclassgroups)) + list(vars(cidlineclasses))

__all__ = __dir__()
