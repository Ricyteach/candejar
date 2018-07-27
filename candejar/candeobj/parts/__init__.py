# -*- coding: utf-8 -*-

"""Sub package for Cande problem atomic parts."""

import types

from .level3 import Node, Element, Boundary


############################
#  Cande Item converters   #
############################

# TODO: replace types.SimpleNamespace kwarg converters with cool types that do stuff
# TODO: maybe make these more robust so filters out unnecessary keyword arguments...?

PipeGroup = types.SimpleNamespace
Node = Node
Element = Element
PipeElement = Element
SoilElement = Element
InterfElement = Element
Boundary = Boundary
Material = types.SimpleNamespace
Factor = types.SimpleNamespace


