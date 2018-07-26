#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `candejar.candeobj.PipeGroupComponent` subclasses."""

import pytest

from candejar.candeobj.parts.bases import CandeStr, CandeNum

zero=CandeNum(0)
BASIC=CandeStr("BASIC")
ALUMINUM=CandeStr("ALUMINUM")
STEEL=CandeStr("STEEL")
PLASTIC=CandeStr("PLASTIC")
GENERAL=CandeStr("GENERAL")
SMOOTH=CandeStr("SMOOTH")
PROFILE=CandeStr("PROFILE")


from candejar.candeobj.parts.pipe_group_components import CandeComponent, PipeGroupComponent, PipeGroupGeneralComponent, \
    BasicComponent, AluminumComponent, SteelComponent, PlasticComponent, \
    Basic1Component, Basic2Component,\
    Plastic1Component, Plastic1GeneralComponent, Plastic1SmoothComponent, Plastic1ProfileComponent,\
    Plastic2Component, Plastic3bAProfileComponent,Plastic3DLRFDComponent, Plastic3DWSDComponent, Plastic3GeneralComponent,\
    Plastic3ProfileComponent, Plastic3SmoothComponent, Plastic4DSmoothLRFDComponent
from candejar.cid import A2, B1Basic, B2Basic, \
    B1Plastic, B2Plastic, B3PlasticAGeneral, B3PlasticAProfile, B3PlasticASmooth, B3PlasticDLRFD, B3PlasticDWSD, B3bPlasticAProfile, B4Plastic

def test_pipegroup_component():
    assert CandeComponent.getsubcls("PipeGroupComponent") is PipeGroupComponent
    assert PipeGroupComponent.getsubcls(A2) is PipeGroupGeneralComponent

def test_pipegroup_component_instances():
    assert type(PipeGroupGeneralComponent(BASIC,zero)) is BasicComponent
    assert type(PipeGroupGeneralComponent(STEEL,zero)) is SteelComponent
    assert type(PipeGroupGeneralComponent(ALUMINUM,zero)) is AluminumComponent
    assert type(PipeGroupGeneralComponent(PLASTIC,zero)) is PlasticComponent

def test_basic_pipegroup_components():
    assert PipeGroupGeneralComponent.getsubcls(BASIC) is BasicComponent
    assert PipeGroupComponent.getsubcls(B1Basic) is Basic1Component
    assert PipeGroupComponent.getsubcls(B2Basic) is Basic2Component

def test_basic_pipegroup_component_instances():
    assert BasicComponent().type_==BASIC
    assert Basic1Component()
    assert Basic2Component()

def test_aluminum_pipegroup_components():
    assert PipeGroupGeneralComponent.getsubcls(ALUMINUM) is AluminumComponent

def test_aluminum_pipegroup_component_instances():
    assert AluminumComponent().type_==ALUMINUM

def test_steel_pipegroup_components():
    assert PipeGroupGeneralComponent.getsubcls(STEEL) is SteelComponent

def test_steel_pipegroup_component_instances():
    assert SteelComponent().type_==STEEL

def test_plastic_pipegroup_components():
    assert PipeGroupGeneralComponent.getsubcls(PLASTIC) is PlasticComponent
    assert PipeGroupComponent.getsubcls(B1Plastic) is Plastic1Component
    assert Plastic1Component.getsubcls(GENERAL) is Plastic1GeneralComponent
    assert Plastic1Component.getsubcls(SMOOTH) is Plastic1SmoothComponent
    assert Plastic1Component.getsubcls(PROFILE) is Plastic1ProfileComponent
    assert PipeGroupComponent.getsubcls(B2Plastic) is Plastic2Component
    assert PipeGroupComponent.getsubcls(B3PlasticDWSD) is Plastic3DWSDComponent
    assert PipeGroupComponent.getsubcls(B3PlasticDLRFD) is Plastic3DLRFDComponent
    assert PipeGroupComponent.getsubcls(B3PlasticAProfile) is Plastic3ProfileComponent
    assert PipeGroupComponent.getsubcls(B3bPlasticAProfile) is Plastic3bAProfileComponent
    assert PipeGroupComponent.getsubcls(B3PlasticASmooth) is Plastic3SmoothComponent
    assert PipeGroupComponent.getsubcls(B3PlasticAGeneral) is Plastic3GeneralComponent
    assert PipeGroupComponent.getsubcls(B4Plastic) is Plastic4DSmoothLRFDComponent

def test_plastic_pipegroup_component_instances():
    assert PlasticComponent().type_==PLASTIC
    with pytest.raises(TypeError):
        assert Plastic1Component()
    assert type(Plastic1Component(GENERAL)) is Plastic1GeneralComponent
    assert type(Plastic1Component(SMOOTH)) is Plastic1SmoothComponent
    assert type(Plastic1Component(PROFILE)) is Plastic1ProfileComponent
    assert Plastic1GeneralComponent().walltype==GENERAL
    assert Plastic1SmoothComponent().walltype==SMOOTH
    assert Plastic1ProfileComponent().walltype==PROFILE
    assert Plastic2Component()
    assert Plastic3DWSDComponent()
    assert Plastic3DLRFDComponent()
    assert Plastic3ProfileComponent()
    assert Plastic3bAProfileComponent()
    assert Plastic3SmoothComponent()
    assert Plastic3GeneralComponent()
    assert Plastic4DSmoothLRFDComponent()
