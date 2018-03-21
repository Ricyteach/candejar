# -*- coding: utf-8 -*-

"""Load `ciddefs.yml` file into objects."""
import yaml
from pathlib import Path

def load_yml_objs():
    with Path(__file__).resolve().parents[1].joinpath("cid/ciddefs.yml").open() as f:
        objs = list(yaml.safe_load_all(f))
    return objs
