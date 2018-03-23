# -*- coding: utf-8 -*-

"""Load `ciddefs.yml` file into objects."""
import yaml
from pathlib import Path
import keyword

def isvalid(ident: str) -> bool:
    """Determines if string is valid Python identifier."""

    if not isinstance(ident, str):
        raise TypeError("expected str, but got {!r}".format(type(ident)))

    if not ident.isidentifier():
        return False

    if keyword.iskeyword(ident):
        return False

    if ident in dir(__builtins__):
        return False

    return True

def load_yml_objs():
    with Path(__file__).resolve().parents[1].joinpath("cid/ciddefs.yml").open() as f:
        objs = list(yaml.safe_load_all(f))
    section_dicts = [section[1] for section in objs]
    for section_dict,obj in zip(section_dicts, objs):
        section_dict_replace = dict()
        for dname,d in section_dict.items():
            d_new = {k + ("" if isvalid(k) else "_"):v for k,v in zip((k_old.replace("Ï•", "φ").lower() for k_old in d.keys()), d.values())}
            section_dict_replace[dname] = d_new
        obj[1] = section_dict_replace
    return objs
