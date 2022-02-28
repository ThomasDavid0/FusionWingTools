
from acdesign.aircraft import Plane, Panel, Rib
from .fusion_tools import Component, Document, Sketch, Folder, Parameters, Occurence, Spline, Line, JointOrigin, Joint
from geometry import Points, Point, Quaternion, Transformation
import adsk.core, adsk.fusion
from time import sleep
from typing import List, Tuple, Dict
import numpy as np
from .fusion_rib import create_or_update_rib

app = adsk.core.Application.get()


panel_fusion_mapping = {
    "length":                    lambda p : (0.1 * p.semispan,                             "mm",  ""),
    "desired_root_chord":        lambda p : (0.1 * p.inbd.chord,                           "mm",  ""),
    "desired_tip_chord":         lambda p : (0.1 * p.otbd.chord,                           "mm",  ""),
    "root_incidence":            lambda p : (p.inbd.incidence + p.incidence,               "rad", ""),
    "tip_incidence":             lambda p : (p.otbd.incidence + p.incidence,               "rad", ""),
    "le_sweep":                  lambda p : (0.1 * p.le_sweep_distance,                    "mm",  ""),
    "mean_chord_prop":           lambda p : (0.25,                                         "",    ""),
    "desired_root_section":      lambda p : (0,                                            "",    p.inbd.name),
    "desired_tip_section":       lambda p : (0,                                            "",    p.otbd.name),
    "desired_root_te_thickness": lambda p : (0.1 * p.inbd.te_thickness,                    "mm",  ""),
    "desired_tip_te_thickness":  lambda p : (0.1 * p.otbd.te_thickness,                    "mm",  ""),
}


def dump_fusion_panel_parameters(p: Panel, target: adsk.fusion.UserParameters) -> Dict[str, adsk.fusion.Parameter]:
    return {key: Parameters.set_or_create(target, key, *value(p)) for key, value in panel_fusion_mapping.items()}


def create_or_update_panel(doc: adsk.core.Document, p: Panel=None):
    
    if p is None:
        uparms = Parameters.get_dict(doc.design.userParameters)
        if not all([key in uparms.keys() for key in panel_fusion_mapping.keys()]):
            raise AttributeError("no Panel passed and some panel parameters missing in target document")
    else:
        uparms = dump_fusion_panel_parameters(p, doc.design.userParameters)
    
    comp=doc.design.rootComponent
    incidence = JointOrigin.get_or_create(
        "incidence",
        comp, 
        comp.originConstructionPoint, 
        comp.yConstructionAxis, 
        comp.xConstructionAxis
    )
    dihedral = JointOrigin.get_or_create(
        "dihedral",
        comp, 
        comp.originConstructionPoint, 
        comp.xConstructionAxis, 
        comp.yConstructionAxis
    )

    root=create_or_update_rib(doc, "root", uparms)
    tip=create_or_update_rib(doc, "tip", uparms)

    rootjoint = Joint.modify(
        Joint.get_or_create(
            "root", 
            comp,
            adsk.fusion.JointGeometry.createByPoint(root.originConstructionPoint), 
            incidence
        ), 
        angle=uparms["root_incidence"].name
    )

    tipjoint = Joint.modify(
        Joint.get_or_create(
            "tip", 
            comp,
            adsk.fusion.JointGeometry.createByPoint(tip.originConstructionPoint), 
            incidence
        ), 
        x=uparms["le_sweep"].name,
        z=uparms["length"].name, 
        angle=uparms["tip_incidence"].name
    )


def parse_fusion_panel_parms(doc: adsk.core.Document) -> Panel:
    parms = Parameters.get_dict(doc.design.userParameters)
    return Panel.create(
        doc.name,
        Point.zeros(),
        0.0,
        0.0,
        False,
        {
            parms["desired_root_section"].coment, 
            parms["desired_root_chord"].value * 10, 
            parms["desired_root_te_thickness"].value * 10
        },
        {
            parms["desired_tip_section"].coment, 
            parms["desired_tip_chord"].value * 10, 
            parms["desired_tip_te_thickness"].value * 10
        },
        parms["le_sweep"].value * 10,
        parms["length"].value * 10
    )









