# -*- coding: utf-8 -*-

"""For creating cande problem objects."""

from pathlib import Path
from typing import Union

from .candeobj.candeobj import CandeObj

def open(path: Union[str, Path]):
    path = Path(path)
    try:
        open_path = {".cid":CandeObj.open, ".cidl3": from_cidl3}[path.suffix.lower()]
    except KeyError:
        raise TypeError(f"{path.suffix!r} file not yet supported") from None
    return open_path(path)

def from_cidl3(path: Path):
    from .cidl3 import candeobj
    return candeobj(path)
