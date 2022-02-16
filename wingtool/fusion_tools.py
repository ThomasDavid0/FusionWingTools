import adsk.core, adsk.fusion, adsk.cam, traceback
app = adsk.core.Application.get()
from geometry import Transformation
import numpy as np

def full_obj_collection(values):
    coll = adsk.core.ObjectCollection.create()
    for value in values:
        coll.add(value)
    return coll


def get_or_create_project(name):
    p = get_project(name)
    if not p:
        return create_project(name)
    else:
        return p


def create_project(name):
    existing_projects = [p.name for p in app.data.dataProjects]
    safename = getsafename(name, lambda n: not n in existing_projects)

    return app.data.dataProjects.add(safename)


def get_project(name):
    for p in app.data.dataProjects:
        if p.name==name:
            return p


def get_or_create_document(name, folder):
    p = get_document(name, folder)
    if not p:
        return create_document(name, folder)
    else:
        return p

def create_document(name, folder = None):
    doc = app.documents.add(0)
    doc.name = name
    if folder:
        doc.saveAs(name, folder, "initial empty document", "")
    return doc

def get_document(name, folder):
    for doc in folder.dataFiles:
        if doc.name==name:
            return doc

    
def get_or_create_component(parent, name: str, transform: Transformation):
    
    occ = parent.occurrences.itemByName(f"{name}:1")
    if occ is None:
        occ =  parent.occurrences.addNewComponent(transform.fusion_matrix3d())
        occ.component.name = name
    else:
        #occ2 = app.activeDocument.design.rootComponent.allOccurrences.itemByName(occ.name)

        #parentocc = app.activeDocument.design.rootComponent.allOccurrences.itemByName(f"{parent.name}:1")
        #if not parentocc is None:
        #    occ = occ.createForAssemblyContext(parentocc)
#
        occ.transform2 = transform.fusion_matrix3d()
        
        #print(np.array(occ2.transform2.asArray()) - np.array(transform.fusion_matrix3d().asArray()))

            
    return occ

def get_or_create_sketch(parent, name, plane, force_create=False):
    sketch = parent.sketches.itemByName(name)

    if sketch is None or force_create:
        sketch = parent.sketches.add(plane) 
        sketch.name=getsafename(name, lambda n: parent.sketches.itemByName(n) is None)
    return sketch


def getsafename(name, namecheckfunc):
    #namecheckfunc returns true when name is free
    i=0
    while True:
        checkname = f"{name}_{i}" if i > 0 else name
        if namecheckfunc(checkname):
            return checkname
        i += 1