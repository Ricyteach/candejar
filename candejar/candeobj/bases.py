# -*- coding: utf-8 -*-

"""Module for working with cande data objects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType, Union, Type, Any

from ..cid import CidLineType
from ..utilities.mixins import ChildRegistryMixin, ClsAttrKeyMakerFactory, CompositeMixin

CandeNum = NewType("CandeNum", int)
CandeFloat = NewType("CandeFloat", float)
CandeStr = NewType("CandeStr", str)
NodeNum = NewType("NodeNum", CandeNum)
StepNum = NewType("StepNum", CandeNum)
MatNum = NewType("MatNum", CandeNum)
CodeNum = NewType("CodeNum", CandeNum)
CandeData = Union[CandeNum, CandeFloat, CandeStr]

LinetypeKeyFactory = ClsAttrKeyMakerFactory("linetype_key")

# TODO: Implement component incorporation with composite design pattern
class CandeComposite(ChildRegistryMixin["CandeComposite"], CompositeMixin):
    """Base class for cande objects (such as pipe groups)

    CandeComposite children are registered with CC by name
    """
    pass

@dataclass
class CandeComponent(ChildRegistryMixin["CandeComponent"]):
    """Base class for components that make up cande objects (such as pipe groups)

    CandeComponent children are registered with CC by name
    """
    @classmethod
    def getsubcls(cls, key: Any) -> Type[CandeComponent]:
        """Get the registered component from the key"""
        return super().getsubcls(key)
