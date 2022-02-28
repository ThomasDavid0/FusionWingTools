

from acdesign.aircraft import Rib
from .fusion_tools import Component, Document, Sketch, Folder, Parameters, Occurence, Spline, Line, JointOrigin, Joint
from geometry import Points, Point, Quaternion, Transformation
import adsk.core, adsk.fusion
from time import sleep
from typing import List, Tuple, Dict
import numpy as np

app = adsk.core.Application.get()



def create_or_update_rib(doc, location: str, uparms: dict):
    
    rib = Rib.create(
        uparms[f"desired_{location}_section"].comment, 
        uparms[f"desired_{location}_chord"].value * 10,
        te_thickness=uparms[f"desired_{location}_te_thickness"].value * 10
    )
    
    occ = Component.get_or_create(doc.design.rootComponent, location, rib.transform)

    base_sec_sketch = Sketch.get_or_create(occ.component, "base_profile", occ.component.xYConstructionPlane)
    Spline.create(rib.points, base_sec_sketch)
    Spline.create(rib.mean_camber() ,Sketch.get_or_create(occ.component, "mean_camber", occ.component.xYConstructionPlane))

    if base_sec_sketch.sketchDimensions.count == 0:
        line = Line.create(Point.zeros(), Point(rib.chord, 0, 0), base_sec_sketch)
        dim = base_sec_sketch.sketchDimensions.addDistanceDimension(
            line.startSketchPoint, 
            line.endSketchPoint, 
            1, 
            Point(rib.chord / 2, 20, 0).fusion_sketch()
        )
        dim.parameter.name = f"{location}_chord"
    else:
        chord = Parameters.find(f"{location}_chord", occ.component.modelParameters)
        chord.value = uparms[f"desired_{location}_chord"].value

    return occ.component

    