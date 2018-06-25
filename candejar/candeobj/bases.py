# -*- coding: utf-8 -*-

"""Module for working with cande data objects."""

from __future__ import annotations
from typing import NewType, Union, TypeVar, Generic, Type

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

CCompSubcls = TypeVar("CCompSubcls", bound="CandeComponent")
CCompSubclsChild = TypeVar("CCompSubclsChild", bound=CCompSubcls)

class CandeComponent(Generic[CCompSubcls], ChildRegistryMixin["CandeComponent"]):
    """Base class for components that make up cande objects (such as pipe groups)

    CandeComponent children are registered with CC by name
    """
    @classmethod
    def getsubcls(cls: Type[CCompSubcls], key: str) -> Type[CCompSubclsChild]:
        """Get the registered component from the key"""
        return super().getsubcls(key)
