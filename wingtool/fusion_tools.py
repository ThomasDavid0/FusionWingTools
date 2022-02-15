import adsk.core, adsk.fusion, adsk.cam, traceback
app = adsk.core.Application.get()
from geometry import Transformation
import numpy as np

def full_obj_collection(values):
    coll = adsk.core.ObjectCollection.create()
    for value in values:
        coll.add(value)
    return coll


def create_document(name):
    doc = app.documents.add(0)
    doc.name = name
    return doc
    
def get_or_create_component(root, name: str, transform: Transformation):
    occ = root.occurrences.itemByName(f"{name}:1")
    if occ is None:
        occ =  root.occurrences.addNewComponent(transform.fusion_matrix3d())
        occ.component.name = name
    else:
        app.activeDocument.design.rootComponent.allOccurrences.itemByName(
            occ.name
        ).transform2 = transform.fusion_matrix3d() 
        
    return occ

def get_or_create_sketch(parent, name, plane):
    sketch = parent.sketches.itemByName(name)
    if sketch is None:
        sketch = parent.sketches.add(plane) 
        sketch.name=name
    return sketch