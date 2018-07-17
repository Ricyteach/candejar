# -*- coding: utf-8 -*-

"""Objects for defining connections between nodes. The nodes can be in the same or different sections."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field, InitVar
from typing import Union, ClassVar, Sequence, Generic, Optional

import abc

from .exc import CandeValueError, CandeTypeError
from ..utilities.collections import KeyedChainView
from .level3 import Node
from ..utilities.descriptors import StandardDescriptor


def check_abc(instance, cls):
    if type(instance) is cls:
        raise CandeTypeError(f"{type(instance).__qualname__!s} class cannot be directly instantiated.")


class ConnectionCategory(enum.Enum):
    """Signifies the type of connection between a group of nodes.

    CANDE only knows about interfaces and links (fixed, pinned, composites: transverse, and longitudinal). Merged is
    internal to Candejar.
    """
    MERGED = 0
    INTERFACE = 1
    # 4 kinds of LINK connections
    FIXED = 8
    PINNED = 9
    # These are also called COMPOSITES
    TRANSVERSE = 10
    LONGITUDINAL = 11


@dataclass
class Tolerance(StandardDescriptor, float):
    """A standard descriptor that stores a tolerance.

    The Tolerance global default is stored as a Tolerance class attribute but
    each Tolerance instance can set its own default. The tolerance for each
    object using the descriptor can be unique.
    """
    default: float = 0.1


@dataclass
class Connection(abc.ABC):
    """Connection parent class for all connection types (merged, interface, and link)."""
    items: Sequence[Node] = field(default_factory=list)  # items is the first argument in the init signature
    tol: float = field(init=False, default=Tolerance())  # descriptor

    def __post_init__(self):
        check_abc(self, Connection)
        if not isinstance(self.category, ConnectionCategory):
            raise CandeTypeError("A valid category attribute is required for the Connection subclass.")

    @property
    @abc.abstractmethod
    def category(self): ...


@dataclass
class MergedConnection(Connection):
    """Merged is a type of connection unique to Candejar and simply "mates" two nodes together that aren't in the same
    section.

    CANDE doesn't know about these; in CANDE they are just the same node.
    """
    category: ClassVar[ConnectionCategory] = ConnectionCategory.MERGED


@dataclass
class PairConnection(Connection):
    """Parent for interface and link connections."""

    def __post_init__(self):
        check_abc(self, PairConnection)
        try:
            i, j = self.items
        except (TypeError, ValueError) as e:
            if len(self.items) != 2:
                raise CandeValueError(f"Only 2 nodes allowed per {type(self).__qualname__!s} object connection") from e
            else:
                raise e
        super().__post_init__()


class SteppedConnection(Connection):
    """Parent for connections with steps."""

    @property
    @abc.abstractmethod
    def step(self): ...


class MaterialedConnection(Connection):
    """Parent for connections with materials."""

    @property
    @abc.abstractmethod
    def mat(self): ...


@dataclass
class InterfaceConnection(PairConnection, MaterialedConnection, SteppedConnection):
    mat: int
    step: int
    category: ClassVar[ConnectionCategory] = ConnectionCategory.INTERFACE


@dataclass
class LinkConnection(PairConnection, SteppedConnection):
    """Parent for link (fixed, pinned, and composite) connections."""

    def __post_init__(self):
        check_abc(self, LinkConnection)
        super().__post_init__()

    def __init_subclass__(cls, **kwargs):
        if cls.category in (ConnectionCategory.FIXED, ConnectionCategory.PINNED) and hasattr(cls, "mat"):
            raise CandeTypeError("Only composite link connections (transverse and longitudinal) have materials.")

    @property
    @abc.abstractmethod
    def death(self): ...


@dataclass
class NonCompositeConnection(LinkConnection):
    death: int = 0

    def __post_init__(self):
        check_abc(self, NonCompositeConnection)
        super().__post_init__()


@dataclass
class FixedConnection(NonCompositeConnection):
    death: int = 0
    category: ClassVar[ConnectionCategory] = ConnectionCategory.FIXED


@dataclass
class PinnedConnection(NonCompositeConnection):
    death: int = 0
    category: ClassVar[ConnectionCategory] = ConnectionCategory.PINNED


@dataclass
class CompositeConnection(LinkConnection, MaterialedConnection):
    mat: int
    death: int = 0


@dataclass
class TransverseConnection(CompositeConnection):
    category: ClassVar[ConnectionCategory] = ConnectionCategory.TRANSVERSE


@dataclass
class LongitudinalConnection(CompositeConnection):
    category: ClassVar[ConnectionCategory] = ConnectionCategory.LONGITUDINAL


class Connections(KeyedChainView[Connection]):
    pass
