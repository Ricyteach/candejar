# -*- coding: utf-8 -*-

"""For creating cande problem objects."""

from pathlib import Path
from typing import Union

from .candeobj.candeobj import CandeObj

def open(path: Union[str, Path]):
    path = Path(path)
    open_path = {'.cid':CandeObj.open, '.cidl3': from_cidl3}[path.suffix.lower()]
    return open_path(path)

def from_cidl3(path: Path):
    from .cidl3 import candeobj
    return candeobj(path)
