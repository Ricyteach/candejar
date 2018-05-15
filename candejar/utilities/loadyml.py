# -*- coding: utf-8 -*-

"""Load `ciddefs.yml` file into objects."""

from typing import Union

import yaml
from pathlib import Path

def load_yml_objs(path: Union[str,Path]):
    with Path(path).open() as f:
        objs = list(yaml.safe_load_all(f))
    return objs
