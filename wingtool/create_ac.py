
from acdesign.aircraft import Plane, Panel, Rib
from .fusion_tools import Component, Document, Sketch, Folder, Parameters, Occurence, Spline, Line, JointOrigin, Joint
from geometry import Points, Point, Quaternion, Transformation
import adsk.core, adsk.fusion
from time import sleep
app = adsk.core.Application.get()

#name, value, units, comment
panelparams = [
    ("length",                      30.0,   "mm",   ""),
    ("desired_root_chord",          15.0,   "mm",   ""),
    ("desired_tip_chord",           10.0,   "mm",   ""),
    ("root_incidence",              0.0,    "deg",  ""),
    ("tip_incidence",               0.0,    "deg",  ""),
    ("le_sweep",                    2.5,    "mm",   ""),
    ("mean_chord_prop",             0.25,   "",     ""),
    ("desired_root_section",        1.0,    "",     "b540ols-il"),
    ("desired_tip_section",         2.0,    "",     "b540ols-il"),
    ("desired_root_te_thickness",   0.05,   "mm",   ""),
    ("desired_tip_te_thickness",    0.05,   "mm",   ""),
]


def create_pdrib(doc, location: str, uparms: dict):
    
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

    
   # if not chord:
   #     chord = Parameters.create(occ.component.modelParameters,f"{location}_chord", rib.chord / 10, "mm", "")
   # else:
   #     
    

def create_panel_doc(doc):
    uparms = Parameters.get_dict(doc.design.userParameters)
    for p in panelparams:
        if not p[0] in uparms.keys():
            Parameters.create(doc.design.userParameters, *p)
    uparms = Parameters.get_dict(doc.design.userParameters)
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

    root=create_pdrib(doc, "root", uparms)
    tip=create_pdrib(doc, "tip", uparms)

    rootjoint = Joint.create(
        "root", 
        comp,
        adsk.fusion.JointGeometry.createByPoint(root.originConstructionPoint), 
        incidence, 
        Point.zeros(),
        uparms["root_incidence"].value
    )

    tipjoint = Joint.create(
        "tip", 
        comp,
        adsk.fusion.JointGeometry.createByPoint(tip.originConstructionPoint), 
        incidence, 
        Point(uparms["le_sweep"].value, 0.0, uparms["length"].value),
        uparms["tip_incidence"].value
    )




















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
