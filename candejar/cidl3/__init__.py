# -*- coding: utf-8 -*-

"""Definition and usage of alternative CIDL3 Cande file format based on YAML."""

from pathlib import Path
from typing import Dict, Union, Any

from .. import CandeObj
from ..utilities.loadyml import load_yml_objs
from ..utilities.mapping_tools import lowerify_mapping

#############################################################################
#                     Top Level CANDE Info Lookups                          #
#############################################################################

# WSD, ASD (same as WSD) or LRFD
METHOD = dict(wsd=0, asd=0, lrfd=1)
# RUN or CHECK
CHECK = dict(run=0, check=1)
# NONE, MINIMIZE, PRINT
BANDWIDTH = dict(none=0, minimize=1, print=2)
# 1: control data, 2: input data,
# 3: created data, 4: maximum
MESHOUTPUT = dict(control=1, input=2, created=3, maximum=4)
# 0: minimal, 1: standard, 2: Duncan,
# 3: interface, 4: MohrCoulomb
RESPONSEOUTPUT = dict(minimal=0, standard=1, duncan=2, interface=3, mohrcoulomb=4)
# 1: Isotropic, 2: Orthotropic, 3: Duncan or Selig, 4: Overburden,
# 5: Extended Hardin, 8: MohrCoulomb
MODEL = dict(isotropic = 1, orthotropic = 2, duncan = 3, selig = 3,
             overburden = 4, extendedhardin = 5, hardin = 5, mohrcoulomb = 8)
# Duncan: 0, Duncan/Selig: 1
DSMODEL = dict(duncan = 0, selig = 1)

TOP_LEVEL_LOOKUPS_TYPE = Dict[str, Dict[str, Union[int, str, Dict[str, Union[int, str]]]]]

TOP_LEVEL_LOOKUPS: TOP_LEVEL_LOOKUPS_TYPE = dict(method = METHOD,
                                                 check = CHECK,
                                                 bandwidth = BANDWIDTH,
                                                 meshoutput = MESHOUTPUT,
                                                 responseoutput = RESPONSEOUTPUT,
                                                 soilmaterials = dict(model = MODEL, dsmodel = DSMODEL),
                                                 )


def candeobj(path:Path) -> CandeObj:
    """Turn a CIDL3 file (YAML formatted) into a cande object"""
    path = Path(path)
    yml_objs = load_yml_objs(path)
    try:
        yml_obj, = yml_objs
    except TypeError as e:
        raise TypeError(f"Invalid: only one file expected in {path.name}, {len(yml_objs)!s} detected")
    candeobj_dict = cidl3_dict_to_candeobj_dict(yml_obj)
    cobj=CandeObj(**candeobj_dict)
    return cobj


def cidl3_dict_to_candeobj_dict(cidl3: Dict[str, Any], *,
               current_lookups=TOP_LEVEL_LOOKUPS) -> Dict[str, Any]:
    if current_lookups is TOP_LEVEL_LOOKUPS:
        cobj_dict = lowerify_mapping(cidl3, recursive=True)
    else:
        cobj_dict = cidl3
    for k, v in cobj_dict.items():
        do_replace(k, v, cobj_dict, current_lookups=current_lookups)
    return cobj_dict


def do_replace(field_name: str, v: Any, cobj_dict: Dict[str, Any], *,
               current_lookups=TOP_LEVEL_LOOKUPS) -> None:
    try:
        lookup = current_lookups[field_name.lower()]
    except KeyError:
        # assume field whose values don't need to be handled
        return
    except AttributeError:
        raise ValueError(f"field name must be str, not {type(field_name).__qualname__}")
    try:
        cobj_dict[field_name] = lookup[v.lower()]
        # field value successfully replaced
        return
    except AttributeError:
        if v in lookup.values():
            # value already valid, doesn't need to be replaced
            return
        if isinstance(v, list):
            # assume v is a list of dictionaries; handle each one
            for i in range(len(v)):
                new_v = cidl3_dict_to_candeobj_dict(v[i], current_lookups=lookup)
                if new_v is not v:
                    v[i] = new_v
            return
    except KeyError:
        pass
    raise ValueError(f"{v!r} invalid for {field_name} field")
