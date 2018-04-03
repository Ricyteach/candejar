# -*- coding: utf-8 -*-

"""Contains the procedure for writing a `CidObj` to a .cid file."""
from dataclasses import asdict, is_dataclass, fields
from pathlib import Path
from typing import Iterator, TypeVar, Mapping, Type, Any, Callable, Sequence, Optional

from .exc import CIDRWError
from ..cid import A2, C3, C4, C5, D1, E1
from ..cidprocessing.main import process as process_cid
from ..cid import CidLine

SEQ_TYPES = {A2: "pipe_groups", C3: "nodes", C4: "elements", C5: "boundaries", D1: "materials", E1: "factors"}

CidObj = TypeVar("CidObj")
CidLineType = Type[CidLine]

def lines(cid: CidObj) -> Iterator[CidLine]:
    i_line_types: Iterator[CidLineType] = process_cid(cid)
    yield from process_lines(cid, i_line_types)

def process_lines(cid: CidObj, i_line_types: Iterator[CidLineType]) -> Iterator[CidLine]:
    while True:
        try:
            line_type: CidLineType = next(i_line_types)
            valid_fields: Sequence[str] = [f.name for f in fields(line_type)]
            target_obj_name: Optional[str] = SEQ_TYPES.get(line_type, "")
            target_obj = getattr(cid, target_obj_name, cid)
            if target_obj is cid:
                target_obj = [target_obj]
            for subobj in target_obj:
                d: Mapping = todict(subobj)
                yield line_type(**{k: v for k, v in d.items() if k in valid_fields})
        except StopIteration:
            break

def todict(o: Any) -> Mapping:
    """Map-ify an object so it can be unpacked as **kwargs to another context."""
    if is_dataclass(o):
        return asdict(o)
    elif isinstance(o, Mapping):
        return o
    else:
        if isinstance(o, type):
            raise CIDRWError("Received command to turn the class instance of {o.__name__!s} to a mapping")
        else:
            return vars(o)

def file(cid: CidObj, path: Path):
    with path.open("w"):
        path.write_text("\n".join(lines(cid)))
