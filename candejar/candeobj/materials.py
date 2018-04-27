# -*- coding: utf-8 -*-

"""Module for working with cande material type objects."""

from dataclasses import dataclass, fields

from .exc import CandeValueError
from ..utilities.mixins import ChildRegistryBase


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


@dataclass
class DuncanSelig(Material):
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
    Angle: float =  0.0  # degrees
    Friction: float =  0.0
    Tensile: float =  1.0  # lbs/in
    Gap: float =  0.0  # in
