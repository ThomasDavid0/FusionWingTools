
from acdesign.aircraft import Plane, Panel, Rib
from .fusion_tools import get_or_create_component, get_or_create_document, get_or_create_sketch, get_or_create_folder, get_item
from geometry import Points, Point, Quaternion
import adsk.core
from time import sleep
app = adsk.core.Application.get()


def create_spline(points: Points, sketch):
    spline_points = (points * Point(1, -1, 0)).fusion_sketch()
    spline = sketch.sketchCurves.sketchFittedSplines.add(spline_points)
    
    try:
        old_spline = sketch.sketchCurves.sketchFixedSplines[0]
        base_profile = old_spline.replaceGeometry(spline.geometry)
    except:
        base_profile = sketch.sketchCurves.sketchFixedSplines.addByNurbsCurve(spline.geometry)    
    spline.deleteMe()


def update_pdrib(doc, location: str, uparms: dict):

    occ = doc.design.rootComponent.occurrences.itemByName(f"{location}:1")
    rib = Rib.create(
        uparms[f"desired_{location}_section"].comment, 
        uparms[f"desired_{location}_chord"].value * 10,
        te_thickness=uparms[f"desired_{location}_te_thickness"].value * 10
    )
    create_spline(rib.points ,occ.component.sketches.itemByName("base_profile"))
    create_spline(rib.mean_camber() ,occ.component.sketches.itemByName("mean_camber"))
    occ.component.modelParameters.itemByName(f"{location}_chord").value = uparms[f"desired_{location}_chord"].value
    

def update_panel_doc(doc):
    uparms = {param.name: param for param in doc.design.userParameters}    
    update_pdrib(doc, "root", uparms)
    update_pdrib(doc, "tip", uparms)























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
    doc.activate()
    self.inbd.create_fusion(doc.design.rootComponent, "inbd")
    self.otbd.create_fusion(doc.design.rootComponent, "otbd")
    doc.save("created wing")
    return doc
    

def create_plane(self: Plane, proj):
    folder = get_or_create_folder("OML", proj.rootFolder)
    doc = get_or_create_document("aircraft", folder)

    self.component = doc.design.rootComponent

    #doc.design.activateRootComponent()
    for panel in self.panels:
        paneldoc = panel.create_fusion(folder)
        
        doc.activate()
        
        gotocc=False
        occ = get_item(panel.name, self.component.occurrences)

        adsk.doEvents()
        sleep(1.0)

        if not occ:
            panel.occurence = self.component.occurrences.addByInsert(
                paneldoc.dataFile,
                panel.transform.fusion_matrix3d(), 
                True
            )
        else:
            pass
            #app.userInterface.activeSelections.add(panel.occurence)
            #app.userInterface.commandDefinitions.itemById('FindInWindow').execute()
        doc.save("panel added")
