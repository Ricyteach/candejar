# -*- coding: utf-8 -*-

"""Dynamically loads CID line classes from `ciddefs.yml`."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any, List

from ..utilities.loadyml import load_yml_objs
from ..utilities.str_tools import isvalid
from .cidline import make_cid_line_cls

CID_DEF_YML_PATH = Path(__file__).resolve().parents[1].joinpath("cid/ciddefs.yml")

def make_cid_line_classes(cid_def_path) -> SimpleNamespace:
    yml_objs = load_yml_objs(Path(cid_def_path))
    section_dicts = [section[1] for section in yml_objs]
    for section_dict,obj in zip(section_dicts, yml_objs):
        section_dict_replace = dict()
        for dname,d in section_dict.items():
            d_new = {k + ("" if isvalid(k) else "_"):v for k,v in zip((k_old.replace("Ï•", "φ").lower() for k_old in d.keys()), d.values())}
            section_dict_replace[dname] = d_new
        obj[1] = section_dict_replace
    line_cls_groups = {name:dct for name,dct in yml_objs}
    line_cls_namespaces = SimpleNamespace(**{name:SimpleNamespace(**{clsname:make_cid_line_cls(clsname, **definitions)
                                                                     for clsname,definitions in line_cls_def.items()})
                                             for name,line_cls_def in line_cls_groups.items()})
    return line_cls_namespaces

cidlineclassgroups = make_cid_line_classes(CID_DEF_YML_PATH)

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
