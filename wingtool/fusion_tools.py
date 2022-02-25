import adsk.core, adsk.fusion, adsk.cam, traceback
app = adsk.core.Application.get()
from geometry import Transformation, Points, Point
import numpy as np
import warnings

def full_obj_collection(values):
    coll = adsk.core.ObjectCollection.create()
    for value in values:
        coll.add(value)
    return coll


def get_item(name, items):
    for doc in items:
        if name in doc.name:
            return doc


def getsafename(name, namecheckfunc):
    #namecheckfunc returns true when name is free
    i=0
    while True:
        checkname = f"{name}_{i}" if i > 0 else name
        if namecheckfunc(checkname):
            return checkname
        i += 1

def get_selected(obj_type):
    for obj in app.userInterface.activeSelections:
        if obj.entity.objectType.split("::")[-1] == obj_type:
            return obj.entity

class Project:
    @staticmethod
    def get_or_create(name):
        p = Project.find(name)
        if not p:
            return Project.create(name)
        else:
            return p

    @staticmethod
    def create(name):
        existing_projects = [p.name for p in app.data.dataProjects]
        safename = getsafename(name, lambda n: not n in existing_projects)

        return app.data.dataProjects.add(safename)
  
    find = staticmethod(lambda name: get_item(name, app.data.dataProjects))


class Document:
    @staticmethod
    def get_or_create(name, folder):
        p = Document.find(name, folder.dataFiles)
        if not p:
            return Document.create(name, folder)
        else:
            return app.documents.open(p)

    @staticmethod
    def create(name, folder = None):
        doc = app.documents.add(0)
        doc.name = name
        if folder:
            doc.saveAs(name, folder, "initial empty document", "")
        return doc

    find = staticmethod(get_item)


class Folder:
    @staticmethod
    def get_or_create(name, folder):
        p = Folder.find(name, folder.dataFolders)
        if not p:
            return Folder.create(name, folder)
        else:
            return p
    
    @staticmethod
    def folder(name, folder):
        existing_folders = [f.name for f in folder.dataFolders]
        safename = getsafename(name, lambda n: not n in existing_folders)
        return folder.dataFolders.add(safename)

    find = staticmethod(get_item)


class Component:
    @staticmethod
    def get_or_create(parent, name: str, transform: Transformation=None):
        occ = parent.occurrences.itemByName(f"{name}:1")
        if occ is None:
            occ =  parent.occurrences.addNewComponent(transform.fusion_matrix3d())
            occ.component.name = name
        else:
            if transform is not None:
                occ.transform = transform.fusion_matrix3d()
                    
        return occ


class Sketch:
    @staticmethod
    def get_or_create(parent, name, plane, force_create=False):
        sketch = parent.sketches.itemByName(name)

        if sketch is None or force_create:
            sketch = parent.sketches.add(plane) 
            sketch.name=getsafename(name, lambda n: parent.sketches.itemByName(n) is None)
        return sketch

    @staticmethod
    def find(name, location):
        return location.sketches.itemByName(name)


class Parameters:
    def get_dict(location):
        return {param.name: param for param in location}  

    def find(name, location):
        return location.itemByName(name)

    def create(location, name, value, units, comment):
        parm = Parameters.find(name, location)
        if parm:
            if not parm.unit == units:
                warnings.warn("cant do parameter unit change here")
            parm.value = value
        else:
            location.add(name, adsk.core.ValueInput.createByReal(value), units, comment)

    

class Spline:
    @staticmethod
    def create(points: Points, sketch):
        spline_points = (points * Point(1, -1, 0)).fusion_sketch()
        spline = sketch.sketchCurves.sketchFittedSplines.add(spline_points)
        
        try:
            old_spline = sketch.sketchCurves.sketchFixedSplines[0]
            base_profile = old_spline.replaceGeometry(spline.geometry)
        except:
            base_profile = sketch.sketchCurves.sketchFixedSplines.addByNurbsCurve(spline.geometry)    
        spline.deleteMe()
        return base_profile
        

class Line:
    @staticmethod
    def create(start, end, sketch):
        start = (start * Point(1, -1, 0)).fusion_sketch() 
        end = (end * Point(1, -1, 0)).fusion_sketch() 

        try:
            line = sketch.sketchCurves.sketchLines[0]
            #line.startSketchPoint = start
            #line.endSketchPoint = end
        except:
            line = sketch.sketchCurves.sketchLines.addByTwoPoints(start, end)
        return line

class Occurence:
    @staticmethod
    def find(name, location):
        return location.occurrences.itemByName(name)



class JointOrigin:
    @staticmethod
    def find(name, location):
        return location.jointOrigins.itemByName(name)
    
    @staticmethod
    def create(name, location, origin, zaxis, xaxis):
        jorigin = location.jointOrigins.add(
            location.jointOrigins.createInput(
                adsk.fusion.JointGeometry.createByPoint(
                    origin
            ))
        )
        jorigin.timelineObject.rollTo(True)
        jorigin.zAxisEntity = zaxis
        jorigin.xAxisEntity = xaxis
        location.parentDesign.timeline.moveToEnd()
        jorigin.name = name

    @staticmethod
    def get_or_create(name, location, origin, zaxis, xaxis):
        jo = JointOrigin.find(name, location)
        if jo:
            return jo
        return JointOrigin.create(name, location, origin, zaxis, xaxis)


class Joint:
    @staticmethod
    def find(name, location):
        return location.joints.itemByName(name)
    
    @staticmethod
    def create(name, location, o1, o2, off: Point, rott: float):
        ji=location.joints.createInput(o1, o2)
        ji.setAsRigidJointMotion()
        ji.offset = adsk.core.ValueInput.createByObject(off.fusion_sketch())
        ji.angle =  adsk.core.ValueInput.createByReal(rott)
        j = location.joints.add(ji)

    @staticmethod
    def get_or_create(name, location, o1, o2, off: Point, rott: float):
        jo = Joint.find(name, location)
        if jo:
            return jo
        return Joint.create(name, location, o1, o2, off, rott)
