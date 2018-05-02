# -*- coding: utf-8 -*-

"""Module for working with cande data objects."""

from typing import NewType, Union

from utilities.mixins import Composite
from ..utilities.mixins import ChildRegistryMixin, ClsAttrKeyMakerFactory

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
class CandeComposite(ChildRegistryMixin, Composite):
    """Base class for cande objects (such as pipe groups)

    CandeComposite children are registered with CC by name
    """
    pass

class CandeComponent(ChildRegistryMixin):
    """Base class for components that make up cande objects (such as pipe groups)

    CandeComponent children are registered with CC by name
    """
    pass
