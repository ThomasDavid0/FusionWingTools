
from acdesign.aircraft import Plane, Panel, Rib
from .fusion_tools import get_or_create_component, get_or_create_document, get_or_create_sketch
from geometry import Points, Point, Quaternion


def create_rib(self: Rib, parent, name: str):
    occurrence = get_or_create_component(parent, name,  self.transform)
    self.component = occurrence.component
    sketch = get_or_create_sketch(self.component, self.name, self.component.xYConstructionPlane, True)
    
    spline_points = (self.points * Point(1, -1, 0)).fusion_sketch()
    spline = sketch.sketchCurves.sketchFittedSplines.add(spline_points)
    
    self.base_sketch = get_or_create_sketch(self.component, "base_profile", self.component.xYConstructionPlane)

    try:
        old_spline = self.base_sketch.sketchCurves.sketchFixedSplines[0]
        self.base_profile = old_spline.replaceGeometry(spline.geometry)
    except:
        self.base_profile = self.base_sketch.sketchCurves.sketchFixedSplines.addByNurbsCurve(spline.geometry)    
    sketch.deleteMe()
    

    #line = sketch.sketchCurves.sketchLines.addByTwoPoints(spline_points[0], spline_points[-1])


def create_panel(self: Panel, folder):
    doc = get_or_create_document(self.name, folder)

    self.inbd.create_fusion(doc.design.rootComponent, "inbd")
    self.otbd.create_fusion(doc.design.rootComponent, "otbd")
    doc.save("initial creation")
    return doc


def create_plane(self: Plane, proj):
    folder = proj.rootFolder.dataFolders.add("OML")

    doc = get_or_create_document("aircraft", folder)

    self.component = doc.design.rootComponent


    #doc.design.activateRootComponent()
    for panel in self.panels:
        paneldoc = panel.create_fusion(folder)
        doc.activate()
        panel.occurence = self.component.occurrences.addByInsert(
            paneldoc.dataFile, 
            panel.transform.fusion_matrix3d(), 
            True
        )
        paneldoc.close()
    doc.save("panels created")


    
    

