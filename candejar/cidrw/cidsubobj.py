# -*- coding: utf-8 -*-

"""CID sub object module for working with the sub objects in a CID sub object sequence (pipe groups, nodes, etc)."""

from dataclasses import field, fields, asdict, dataclass
from typing import Generic, List, Type, Iterator, Union, TypeVar

from ..cid import CidLine, CidSubLine
from .exc import CIDRWError
from ..utilities.collections import MyCounter
from .. import fea


# TODO: Delete this module? Rework references to contained `CidObj`s to return a `SimpleNamespace` subclass on the fly.
# The `SimpleNamespace` would just be a current view of the combined attributes from the relevant file `CidLine`s.
# Could do away with all code below except `iter_line_objs`. Code for `iter_line_objs` would be identical except
# need to accept `idx` parameter for object of interest.


CidData = Union[int, float, str]
CidObj = TypeVar("CidObj")
CidSeq = TypeVar("CidSeq")


@dataclass(eq=False)
class CidSubObj(Generic[CidObj, CidSeq, CidSubLine, fea.FEAObj]):
    """A viewer object that gets its data from the `CidLine` objects in `.cid_obj`."""

    def make_fea(self) -> fea.FEAObj:
        if type(self.container).__name__ == "SoilMaterials":
            breakpoint()
        field_names: List[str] = [f.name for f in fields(self.container.type_)]
        # TODO: major bug below, currently: most fields/attributes for Material and PipeGroup objects are being lost;
        # need to think of a way to fix
        return self.container.type_(**{k:v for line_obj in self.iter_line_objs for k,v in asdict(line_obj).items() if k in field_names})

    container: CidSeq = field(repr=False)
    idx: int = field(repr=False)
    fea_obj: fea.FEAObj = field(default=property(make_fea), init=False)

    @property
    def cid_obj(self) -> CidObj:
        return self.container.cid_obj

    @property
    def line_type(self) -> Type[CidLine]:
        return self.container.line_type

    @property
    def iter_line_objs(self) -> Iterator[CidSubLine]:
        i_line_objs = iter(self.cid_obj.line_objs)
        num = self.idx + 1
        start_ctr = MyCounter()
        for line in i_line_objs:
            start_ctr[isinstance(line, self.line_type)] += 1
            if start_ctr[True] == num:
                yield line
                break
        else:
            raise CIDRWError(f"Could not locate {self.line_type.__name__!s} object number {num!s}")
        for line in i_line_objs:
            if not isinstance(line, self.line_type):
                yield line
            else:
                break

    def __getattr__(self, attr: str) -> CidData:
        for line_obj in self.iter_line_objs:
            try:
                return getattr(line_obj, attr)
            except AttributeError:
                continue
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {attr!r}")
