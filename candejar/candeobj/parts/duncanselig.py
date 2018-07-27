# -*- coding: utf-8 -*-

"""Module for working with cande material type objects."""

from dataclasses import dataclass
from typing import ClassVar, Optional

from .materials import Material
from ..exc import CandeError
from ...utilities.descriptors import CannedObjects
from ...utilities.mixins import ChildAsAttributeMixin

CannedMaterials = CannedObjects[Material]


class DuncanSeligError(CandeError):
    pass


class DuncanSeligValueError(DuncanSeligError, ValueError):
    pass


class DuncanSeligInstanceError(DuncanSeligError, AttributeError):
    pass


@dataclass
class DuncanSeligBase(Material):
    """Base class for all Duncan/Selig soil materials."""
    # D1
    model: int = 3
    # D2
    lrfdcontrol: int = 0
    # 1.0 for in-situ materials
    moduliaveraging: float = 0.5
    # Duncan: 0, Dancan/Selig: 1
    dsmodel: int = 1
    # Original: 0, Unloading: 1
    unloading: int = 1

    def __post_init__(self):
        if type(self) is DuncanSeligBase:
            raise DuncanSeligError("Cannot instantiate DuncanSeligBase "
                                   "directly; use Duncan, Selig, or "
                                   "DuncanSeligCustom")
        super().__post_init__()


@dataclass
class DuncanSeligCanned(DuncanSeligBase):
    """Base class for pre-canned Duncan/Selig soil materials."""
    _canned: ClassVar[Optional[CannedMaterials]] = None

    def __post_init__(self):
        if type(self) is DuncanSeligCanned:
            raise DuncanSeligError("Cannot instantiate DuncanSeligCanned "
                                   "directly; use Duncan or Selig")
        super().__post_init__()
        # 1 or 0 for dsmodel number
        try:
            valid_names = [DUNCAN_MODELS, SELIG_MODELS][self.dsmodel]
        except IndexError:
            raise DuncanSeligValueError(f"Invalid dsmodel number: {self.dsmodel!s} "
                                        f"for {type(self).__name__} object; use "
                                        f"0 (Duncan) or 1 (Selig)") from None
        # only pre-canned names allowed for canned DS models
        if self.name not in valid_names:
            raise DuncanSeligValueError(f"Invalid canned model name: {self.name!r} ")


DUNCAN_MODELS = ('CA105 CA95 CA90 '
                 'SM100 SM90 SM85 '
                 'SC100 SC90 SC85 '
                 'CL100 CL90 CL85').split()


@dataclass
class Duncan(DuncanSeligCanned, ChildAsAttributeMixin):
    """For pre-canned Duncan soil materials."""
    _canned: ClassVar[CannedMaterials] = CannedObjects(DUNCAN_MODELS)
    dsmodel: int = 0


SELIG_MODELS = ('SW100 SW95 SW90 SW85 SW80 '
                'ML95 ML90 ML85 ML80 ML50 '
                'CL95 CL90 CL85 CL80').split()

# init duncan canned models
DuncanCanned = Duncan._canned


@dataclass
class Selig(DuncanSeligCanned, ChildAsAttributeMixin):
    """For pre-canned Selig soil materials."""
    _canned: ClassVar[CannedMaterials] = CannedObjects(SELIG_MODELS)
    dsmodel: int = 1


# init selig canned models
SeligCanned = Selig._canned


@dataclass
class DuncanSelig(DuncanSeligBase):
    """For custom Duncan/Selig soil materials."""
    # D3
    cohesion: float = 0.0  # psi
    phi_i: float = 0.0  # degrees
    delta_phi: float = 0.0  # degrees
    modulus_i: float = 0.0
    modulus_n: float = 0.0
    ratio: float = 0.0
    # D4
    bulk_i: float = 0.0
    bulk_m: float = 0.0
    poissons: float = 0.0

    def __post_init__(self):
        super().__post_init__()
        # 1 or 0 for dsmodel number
        try:
            invalid_names = [DUNCAN_MODELS, SELIG_MODELS][self.dsmodel]
        except IndexError:
            raise DuncanSeligValueError(f"Invalid dsmodel number: {self.dsmodel!s} "
                                        f"for {type(self).__name__} object; use "
                                        f"0 (Duncan) or 1 (Selig)") from None
        # pre-canned names aren't allowed for custom DS models
        if self.name in invalid_names:
            raise DuncanSeligValueError(f"Invalid user model name: {self.name!r} ")
