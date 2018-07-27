# -*- coding: utf-8 -*-

"""Module for working with cande material type objects."""

from dataclasses import dataclass, fields

from ..exc import CandeValueError
from ...utilities.mixins import ChildRegistryMixin


@dataclass
class Material(ChildRegistryMixin):
    # 1: Isotropic, 2: Orthotropic, 3: Duncan/Selig, 4: Overburden,
    # 5: Extended Hardin, 6: Interface, 7: Composite Link, 8: Mohr/Coulomb
    model: int
    density: float = 0.0
    name: str = ""
    # layers: InitVar[Sequence[Layer]] = None <- will use for overburden soil implementation if ever needed

    def __post_init__(self):
        # Material subclasses must have the correct (default) model number
        if type(self) is not Material:
            model_num = {f.name: f.default for f in fields(self)}["model"]
            if self.model != model_num:
                raise CandeValueError(f"model = {model_num!s}; "
                                      f"{type(self).__name__} model field "
                                      f"cannot be changed to {self.model!s}")


@dataclass
class Isotropic(Material):
    # D1
    model: int = 1
    # D2
    modulus: float = 0.0  # psi
    poissons: float = 0.0


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
    angle: float = 0.0  # degrees
    friction: float = 0.0
    tensile: float = 1.0  # lbs/in
    gap: float = 0.0  # in


@dataclass
class Composite(Material):
    # D2
    group1: int = 0
    group2: int = 0
    fraction: float = 0
    # D1
    model: int = 7
