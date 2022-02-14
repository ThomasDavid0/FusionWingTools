import adsk.core, adsk.fusion, adsk.cam, traceback
from .airfoil_points import AirfoilPoints
from acdesign.aircraft import Plane, Panel, Rib

app = adsk.core.Application.get()

def object_collection_from_list(values):
    coll = adsk.core.ObjectCollection.create()
    for value in values:
        coll.add(value)
    return coll

def create_document(name):
    doc = app.documents.add(0)
    doc.name = name
    return doc, doc.design.rootComponent


def create_xy_plane(component, offset):
    planeinput = component.constructionPlanes.createInput()
    offsetValue = adsk.core.ValueInput.createByReal(offset)
    planeinput.setByOffset(component.xYConstructionPlane, offsetValue)
    return component.constructionPlanes.add(planeinput)

def create_sketch(component, plane, name):
    sketch = component.sketches.add(plane)
    sketch.name = name
    return sketch

def fusion_point(point):
    return adsk.core.Point3D.create(*(0.1 * point).to_list())

def create_points(points):
    return object_collection_from_list([fusion_point(pos) for pos in points])


def create_rib(component, rib, name):
    plane = create_xy_plane(component, rib.pos.z)
    sketch = create_sketch(component, plane, rib.name)
    spline = sketch.sketchCurves.sketchFittedSplines.add(create_points(afpoints.positions))
    te_line = sketch.sketchCurves.sketchLines.addByTwoPoints(
        spline.fitPoints.item(0), spline.fitPoints.item(spline.fitPoints.count-1)
    )
    return sketch

def create_panel(doc, panel: Panel):
    pass