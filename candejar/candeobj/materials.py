# -*- coding: utf-8 -*-

"""Module for working with cande material type objects."""

from dataclasses import dataclass, fields, make_dataclass, field
from typing import ClassVar, Type, Any, Optional

from .exc import CandeError, CandeValueError
from ..utilities.mixins import ChildRegistryBase, ChildAsAttributeBase

class DuncanSeligError(CandeError):
    pass

class DuncanSeligValueError(DuncanSeligError, ValueError):
    pass

class DuncanSeligInstanceError(DuncanSeligError, AttributeError):
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
class DuncanSeligBase(Material):
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
        if type(self) is DuncanSeligBase:
            raise DuncanSeligError("Cannot instantiate DuncanSeligBase "
                                   "directly; use Duncan, Selig, or "
                                   "DuncanSeligCustom")
        super().__post_init__()

class CannedObjects:
    """A namespace holding references to canned material instances"""
    def __init__(self, child_names):
        self._child_names = child_names
    def __set_name__(self, owner: Type[Material], name: str) -> None:
        self._cls: Type[Material] = owner
        self._init_incomplete = object() # sentinel for no canned objects yet
    def __get__(self, instance: Material, owner: Type[Material]) -> "CannedObjects":
        # initialize all the instances
        if getattr(self, "_init_incomplete", None):
            for i in self._child_names:
                setattr(self, i, self.get_subclass(i))
            del self._init_incomplete
        return self
    def get_subclass(self, canned_name: str) -> Type[Material]:
        """New dataclass with the correct default values for canned material"""
        return make_dataclass(canned_name,
                              [("name", str, field(default=canned_name)),],
                              bases=(self._cls,))
    def __getattr__(self, canned_name: str) -> Any:
        if canned_name in self._child_names:
            raise DuncanSeligInstanceError(f"The {type(self).__name__!s} object "
                                           f"{canned_name!s} has not been initialized")
        else:
            raise AttributeError(f"")

@dataclass
class DuncanSeligCanned(DuncanSeligBase):
    _canned: ClassVar[Optional[CannedObjects]] = None
    def __post_init__(self):
        if type(self) is DuncanSeligCanned:
            raise DuncanSeligError("Cannot instantiate DuncanSeligCanned "
                                   "directly; use Duncan or Selig")
        super().__post_init__()
        try:
            valid_names = [DUNCAN_MODELS, SELIG_MODELS][self.dsmodel]
        except IndexError:
            raise DuncanSeligValueError(f"Invalid dsmodel number: {self.dsmodel!s} "
                                        f"for {type(self).__name__} object; use "
                                        f"0 (Duncan) or 1 (Selig)") from None
        if self.name not in valid_names:
            raise DuncanSeligValueError(f"Invalid canned model name: {self.name!r} ")


DUNCAN_MODELS = ('CA105 CA95 CA90 '
                 'SM100 SM90 SM85 '
                 'SC100 SC90 SC85 '
                 'CL100 CL90 CL85').split()

@dataclass
class Duncan(DuncanSeligCanned, ChildAsAttributeBase):
    _canned: ClassVar[CannedObjects] = CannedObjects(DUNCAN_MODELS)
    dsmodel: int = 0

SELIG_MODELS = ('SW100 SW95 SW90 SW85 SW80 '
                'ML95 ML90 ML85 ML80 ML50 '
                'CL95 CL90 CL85 CL80').split()

# init duncan canned models
DuncanCanned = Duncan._canned

@dataclass
class Selig(DuncanSeligCanned, ChildAsAttributeBase):
    _canned: ClassVar[CannedObjects] = CannedObjects(SELIG_MODELS)
    dsmodel: int = 1

# init selig canned models
SeligCanned = Selig._canned

@dataclass
class DuncanSelig(DuncanSeligBase):
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

    def __post_init__(self):
        super().__post_init__()
        try:
            invalid_names = [DUNCAN_MODELS, SELIG_MODELS][self.dsmodel]
        except IndexError:
            raise DuncanSeligValueError(f"Invalid dsmodel number: {self.dsmodel!s} "
                                        f"for {type(self).__name__} object; use "
                                        f"0 (Duncan) or 1 (Selig)") from None
        if self.name in invalid_names:
            raise DuncanSeligValueError(f"Invalid user model name: {self.name!r} ")


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
