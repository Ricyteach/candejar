# -*- coding: utf-8 -*-

"""Load `ciddefs.yml` file into objects."""
import yaml
from pathlib import Path

def load_yml_objs():
    with Path(__file__).resolve().parents[1].joinpath("cid/ciddefs.yml").open() as f:
        objs = list(yaml.safe_load_all(f))
    o = objs[-1][1]
    if any("Ï•" in k for d in o.values() for k in d.keys()):
        d_replace = dict()
        for dname,d in o.items():
            for k in d.keys():
                k_new = k.replace("Ï•", "ϕ")

    return objs
