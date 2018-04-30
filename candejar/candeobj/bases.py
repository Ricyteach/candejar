# -*- coding: utf-8 -*-

"""Module for working with cande data objects."""

from typing import NewType, Union

CandeNum = NewType("CandeNum", int)
CandeFloat = NewType("CandeFloat", float)
CandeStr = NewType("CandeStr", str)
NodeNum = NewType("NodeNum", CandeNum)
StepNum = NewType("StepNum", CandeNum)
MatNum = NewType("MatNum", CandeNum)
CodeNum = NewType("CodeNum", CandeNum)
CandeData = Union[CandeNum, CandeFloat, CandeStr]
