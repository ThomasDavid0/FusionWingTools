import adsk.core, adsk.fusion, adsk.cam, traceback
app = adsk.core.Application.get()
from geometry import Transformation, Point, Quaternion
from acdesign.aircraft import Plane, Panel, Rib
from itertools import chain

def create_document(name):
    doc = app.documents.add(0)
    doc.name = name
    return doc


def create_matrix3d(transform: Transformation):
    matr =  adsk.core.Matrix3D.create()
    matd = transform.to_matrix().T.tolist()

    if matr.setWithArray(list(chain(*matd))):
        return matr
    else:
        raise Exception("couldnt set the transformation")


def create_component(root, name: str, transform: Transformation):
    occ =  root.occurrences.addNewComponent(create_matrix3d(transform))
    occ.component.name  = name
    return occ.component 


def full_obj_collection(values):
    coll = adsk.core.ObjectCollection.create()
    for value in values:
        coll.add(value)
    return coll

def create_sketch_point(point):
    return adsk.core.Point3D.create(*(point))

def create_sketch_points(points):
    return full_obj_collection([create_sketch_point(p) for p in points])

def create_rib(parent, rib: Rib):
    component = create_component(parent, rib.name,  rib.transform)

    sketch = component.sketches.add(component.xYConstructionPlane) 

    spline_points = create_sketch_points(rib.points)
    spline = sketch.sketchCurves.sketchFittedSplines.add(spline_points)

    #line = sketch.sketchCurves.sketchLines.addByTwoPoints(spline_points[0], spline_points[-1])

    return component

def create_panel(parent, panel: Panel):
    component = create_component(parent, panel.name,  panel.transform)
    inbd = create_rib(component, panel.inbd.rename(f"{panel.name}_inbd_{panel.inbd.name}"))
    otbd = create_rib(component, panel.otbd.rename(f"{panel.name}_otbd_{panel.otbd.name}"))
    return component

def create_plane(plane):
    doc = create_document(plane.name)
    panel_component = create_panel(doc.design.rootComponent, plane.panels[0])
    
    return doc