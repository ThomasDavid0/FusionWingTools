

from acdesign.aircraft import Rib
from .fusion_tools import Component, Document, Sketch, Folder, Parameters, Occurence, Spline, Line, JointOrigin, Joint
from geometry import Points, Point, Quaternion, Transformation
import adsk.core, adsk.fusion
from time import sleep
from typing import List, Tuple, Dict
import numpy as np

app = adsk.core.Application.get()


def parse_rib_parms(doc, location):
    return Rib.create(
        Parameters.find(f"desired_{location}_section", doc.design.userParameters).comment, 
        Parameters.find(f"desired_{location}_chord", doc.design.userParameters).value * 10,
        te_thickness=Parameters.find(f"desired_{location}_te_thickness", doc.design.userParameters).value * 10
    )


class FusionRib:
    def __init__(self, doc: adsk.core.Document, location: str):
        self.doc=doc
        self.location = location
        
        self.rib = Rib.parse_parameters(self.doc, location)
        self.occ = Component.get_or_create(
            self.doc.design.rootComponent, 
            self.location, 
            self.rib.transform
        )

        self.ocp = self.occ.component.originConstructionPoint

        self.base_sec_sketch = Sketch.get_or_create(
            self.occ.component, 
            "base_profile", 
            self.occ.component.xYConstructionPlane
        )

        self.base_sec_spline = Spline.create(self.rib.points, self.base_sec_sketch)

        self.mean_camber_sketch = Sketch.get_or_create(
            self.occ.component, 
            "mean_camber", 
            self.occ.component.xYConstructionPlane
        )

        self.mean_camber_spline = Spline.create(self.rib.mean_camber(), self.mean_camber_sketch)

        self.chord_parm = Parameters.find(f"{location}_chord", self.occ.component.modelParameters)
        if self.chord_parm is None:
            chord_line = Line.create(Point.zeros(), Point(self.rib.chord, 0, 0), self.base_sec_sketch)
            dim = self.base_sec_sketch.sketchDimensions.addDistanceDimension(
                chord_line.startSketchPoint, 
                chord_line.endSketchPoint, 
                1, 
                Point(self.rib.chord / 2, 20, 0).fusion_sketch_point()
            )
            dim.parameter.name = f"{location}_chord"
            self.chord_parm = Parameters.find(f"{location}_chord", self.occ.component.modelParameters)
        else:
            self.chord_parm.value = Parameters.find(
                f"desired_{location}_chord", 
                self.doc.design.userParameters
            ).value

        
