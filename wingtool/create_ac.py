
from acdesign.aircraft import Plane, Panel, Rib
from .fusion_tools import get_or_create_component, create_document, get_or_create_sketch
from geometry import Points, Point


def create_rib(self: Rib, parent, name: str):
    occurrence = get_or_create_component(parent, name,  self.transform)
    self.component = occurrence.component
    self.sketch = get_or_create_sketch(self.component, self.name, self.component.xYConstructionPlane, True)
    
    spline_points = (self.points * Point(1, -1, 0)).fusion_sketch()
    spline = self.sketch.sketchCurves.sketchFittedSplines.add(spline_points)
    spline.isFixed = True
    
    self.base_sketch = get_or_create_sketch(self.component, "base_profile", self.component.xYConstructionPlane)

    try:
        old_spline = self.base_sketch.sketchCurves.sketchFixedSplines[0]
        self.base_profile = old_spline.replaceGeometry(spline.geometry)
    except:
        self.base_profile = self.base_sketch.sketchCurves.sketchFixedSplines.addByNurbsCurve(spline.geometry)    
        
    

    #line = sketch.sketchCurves.sketchLines.addByTwoPoints(spline_points[0], spline_points[-1])


def create_panel(self: Panel, parent):
    occurence = get_or_create_component(parent, self.name,  self.transform)
    occurence.activate()
    self.component = occurence.component
    self.inbd.create_fusion(self.component, "inbd")
    self.otbd.create_fusion(self.component, "otbd")
    

def create_plane(self: Plane, doc):
    self.component = doc.design.rootComponent
    doc.design.activateRootComponent()
    for panel in self.panels:
        panel.create_fusion(self.component)
    

