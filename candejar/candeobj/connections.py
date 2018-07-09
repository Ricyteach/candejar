# -*- coding: utf-8 -*-

"""The map sequence for section node connections and their connection objects ."""

from __future__ import annotations
import enum
from dataclasses import dataclass, field, InitVar
from typing import Union, ClassVar, Sequence, Generic, Any

from .candeseq import CandeSection
from .level3 import Node
from ..utilities.descriptors import StandardDescriptor


@dataclass
class Tolerance(StandardDescriptor):
    """A standard descriptor that stores the distance between two objects.

    The Tolerance global default is stored as a Tolerance class attribute but
    each Tolerance instance can set its own default. The tolerance for each
    object using the descriptor can be unique.
    """
    default: float = 0.1


class ConnectionType(enum.Enum):
    """Signifies the type of connection between a group of nodes.

    CANDE only knows about interface, and the two kinds of links: fixed and
    pinned. Merged is a type of connection unique to Candejar and simply
    "mates" two nodes together that aren't in the same section.
    """
    MERGED = 0
    INTERFACE = 1
    FIXED = 8
    PINNED = 9


V = Union[Node, CandeSection]


@dataclass
class Connection(Generic[V]):
    tol: float = field(init=False)  # for type hinting only
    tol: ClassVar[Tolerance[Connection,V]] = Tolerance()  # descriptor
    items: Sequence[V] = field(default_factory=list)
    type_: InitVar[Union[str, int, ConnectionType]] = 0
    info: Any = None

    def __post_init__(self, type_) -> None:
        if isinstance(type_, str):
            t = ConnectionType[type_]
        else:
            t = ConnectionType(type_)
        self.type_: ConnectionType = t
