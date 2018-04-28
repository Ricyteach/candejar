# -*- coding: utf-8 -*-

"""Module for working with cande material type objects."""

from dataclasses import dataclass, fields, make_dataclass, field
from typing import ClassVar, Tuple, Type

from .exc import CandeValueError
from ..utilities.mixins import ChildRegistryBase


class DuncanSeligValueError(CandeValueError):
    pass


#  TODO: Material objects can contain a wide variety of attributes; need to find a way to accommodate
@dataclass
class Material(ChildRegistryBase):
    model: int  # 1: Isotropic, 2: Orthotropic, 3: Duncan/Selig, 4: Overburden,
                # 5: Extended Hardin, 6: Interface, 7: Composite Link, 8: Mohr/Coulomb
    density: float = 0.0
    name: str = ""
    # layers: InitVar[Sequence[Layer]] = None <- will use for overburden soil implementation if ever needed
    def __post_init__(self):
        # Material subclasses must have the correct (default) model number
        if type(self) is not Material:
            model_num = {f.name:f.default for f in fields(self)}["model"]
            if self.model != model_num:
                raise CandeValueError(f"model = {model_num!s}; {type(self).__name__} model field cannot be changed to {self.model!s}")


@dataclass
class Isotropic(Material):
    # D1
    model: int = 1
    # D2
    modulus: float = 0.0  # psi
    poissons: float = 0.0


DUNCAN_MODELS = ('CA105 CA95 CA90 SM100 SM90 SM85'
                 'SC100 SC90 SC85 CL100 CL90 CL85').split()

SELIG_MODELS = ('SW100 SW95 SW90 SW85 SW80'
                'ML95 ML90 ML85 ML80 ML50'
                'CL95 CL90 CL85 CL80').split()

class CannedObjects:
    """A namespace holding references to canned material instances"""
    def __set_name__(self, owner: Type["DuncanSelig"], name: str) -> None:
        if name not in "duncan selig".split():
            raise DuncanSeligValueError(f"Invalid canned collection name: {name!r}")
        self._inst_names: Tuple[str] = dict(duncan=DUNCAN_MODELS, selig=SELIG_MODELS)[name]
        self._dsmodel: int = dict(duncan=0, selig=1)[name]
        self._cls: Type["DuncanSelig"] = owner
        self._init_incomplete = object()
    def __get__(self, instance: "DuncanSelig", owner: Type["DuncanSelig"]) -> "CannedObjects":
        # initialize all the instances
        if getattr(self, "_init_incomplete", None):
            for i in self._inst_names:
                setattr(self, i, self.get_subclass(i))
            del self._init_incomplete
        return self
    def get_subclass(self, canned_name: str) -> Type["DuncanSelig"]:
        """New dataclass with the correct default values for canned material"""
        return make_dataclass(canned_name,
                              [("name", str, field(default=canned_name)),
                               ("dsmodel", int, field(default=self._dsmodel))],
                              bases=(self._cls,))
    def __getattr__(self, canned_name: str) -> "DuncanSelig":
        if canned_name in self._inst_names:
            return getattr(self, canned_name)
        else:
            raise AttributeError(f"{type(self).__name__!r} object has no "
                                 f"attribute {canned_name!r}")


@dataclass
class DuncanSelig(Material):
    duncan: ClassVar[CannedObjects] = CannedObjects()
    selig: ClassVar[CannedObjects] = CannedObjects()
    # D1
    model: int = 3
    # D2
    lrfdcontrol: int =  0
    # 1.0 for in-situ materials
    moduliaveraging: float =  0.5
    # Duncan: 0, Dancan/Selig: 1
    dsmodel: int =  1
    # Original: 0, Unloading: 1
    unloading: int =  1

    def __post_init__(self):
        super().__post_init__()
        try:
            valid_names = [DUNCAN_MODELS, SELIG_MODELS][self.dsmodel]
        except IndexError:
            raise DuncanSeligValueError(f"Invalid dsmodel number: {self.dsmodel!s} (0: Duncan, 1: Selig") from None
        if self.name not in valid_names and type(self) is DuncanSelig:
            raise DuncanSeligValueError(f"Invalid canned model name: {self.name!r} ")
        elif self.name in valid_names and type(self) is not DuncanSelig:
            raise DuncanSeligValueError(f"Invalid user model name: {self.name!r} ")
        elif type(self) is DuncanSelig:
            # duncan or selig?
            d_or_s = ("duncan", "selig")[self.dsmodel]
            # get canned instance namespace
            canned_objects = getattr(DuncanSelig, d_or_s)
            # get specific canned instance
            d_or_s_canned = getattr(canned_objects, self.name)
            # set obj state to specific canned instance
            self.__dict__ = d_or_s_canned.__dict__


@dataclass
class DuncanSeligCustom(DuncanSelig):
    # D3
    cohesion: float =  0.0 # psi
    phi_i: float =  0.0 # degrees
    delta_phi: float =  0.0 # degrees
    modulus_i: float =  0.0
    modulus_n: float =  0.0
    ratio: float =  0.0
    # D4
    bulk_i: float =  0.0
    bulk_m: float =  0.0
    poissons: float =  0.0


@dataclass
class MohrCoulomb(Material):
    # D1
    model: int = 8
    # D2
    modulus: float = 0.0  # psi
    poissons: float = 0.0
    cohesion: float = 0.0  # psi
    phi: float = 0.0  # degrees


@dataclass
class Interface(Material):
    # D1
    model: int = 6
    # D2
    angle: float =  0.0  # degrees
    friction: float =  0.0
    tensile: float =  1.0  # lbs/in
    gap: float =  0.0  # in
