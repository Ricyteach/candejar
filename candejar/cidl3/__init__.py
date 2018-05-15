# -*- coding: utf-8 -*-

"""Definition and usage of alternative CIDL3 Cande file format based on YAML."""

from pathlib import Path

from .. import CandeObj
from ..utilities.loadyml import load_yml_objs
from ..utilities.mapping_tools import lowerify_mapping

def candeobj(path:Path) -> CandeObj:
    """Turn a CIDL3 file (YAML formatted) into a cande object"""
    path = Path(path)
    yml_objs = load_yml_objs(path)
    try:
        yml_obj, = yml_objs
    except TypeError as e:
        raise TypeError(f"Invalid: only one file expected in {path.name}, {len(yml_objs)!s} detected")
    cobj=CandeObj(**lowerify_mapping(yml_obj, recursive=True))
    return cobj
