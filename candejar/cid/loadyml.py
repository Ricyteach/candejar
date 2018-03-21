# -*- coding: utf-8 -*-

"""Load `ciddefs.yml` file into objects."""
import yaml
from pathlib import Path

def load_yml_objs():
    with Path(__file__).resolve().parents[1].joinpath("cid/ciddefs.yml").open() as f:
        objs = list(yaml.safe_load_all(f))
    pipes = objs[-1][1]
    if any("Ï•" in k for d in pipes.values() for k in d.keys()):
        pipes_replace = dict()
        for dname,d in pipes.items():
            d_new = {k.replace("Ï•", "φ"):v for k,v in d.items()}
            pipes_replace[dname] = d_new
        objs[-1][1] = pipes_replace
    return objs
