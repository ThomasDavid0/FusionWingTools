import adsk.core, adsk.fusion, adsk.cam, traceback
app = adsk.core.Application.get()
from geometry import Transformation, Points, Point
import numpy as np
import warnings
from typing import Union, List
from time import sleep

def full_obj_collection(values):
    coll = adsk.core.ObjectCollection.create()
    for value in values:
        coll.add(value)
    return coll


def get_item(name, items):
    for doc in items:
        if name == doc.name:
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
    def get_or_create(name: str) -> adsk.core.DataProject:
        p = Project.find(name)
        if not p:
            return Project.create(name)
        else:
            return p

    @staticmethod
    def create(name: str) -> adsk.core.DataProject:
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
    def get_or_create(parent, name: str, transform: Transformation=None) -> adsk.fusion.Occurrence:
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

    def find(name, location: Union[adsk.fusion.ModelParameters, adsk.fusion.UserParameters]) -> adsk.fusion.Parameter:
        return location.itemByName(name)

    def set_or_create(location: adsk.core.Base, name, value, units, comment) -> adsk.fusion.Parameter:
        parm = Parameters.find(name, location)
        if parm:
            if not parm.unit == units:
                warnings.warn("cant do parameter unit change here")
            parm.value = value
            parm.comment = comment
        else:
            parm = location.add(name, adsk.core.ValueInput.createByReal(value), units, comment)
        return parm 

    def get_created_by(creator: adsk.core.Base, location: adsk.fusion.Component) -> List[adsk.fusion.Parameter]:
        return [p  for p in location if p.createdBy == creator] 

class Spline:
    @staticmethod
    def create(points: Points, sketch):
        spline_points = (points * Point(1, -1, 0)).fusion_sketch_points()
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
        start = (start * Point(1, -1, 0)).fusion_sketch_point() 
        end = (end * Point(1, -1, 0)).fusion_sketch_point() 

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

    @staticmethod
    def find_by_component(name, location):
        for occ in location.occurrences:
            if len(occ.component.name) >= len(name):
                if name == occ.component.name[:len(name)]:
                    return occ

    @staticmethod
    def insert_component(parent: adsk.fusion.Component, child: adsk.fusion.FusionDocument):
        occ=None
        i=0
        while not occ:
            occ = Occurence.find_by_component(child.design.rootComponent.name, parent)
            if not occ is None or i > 5:
                break
            child.activate()
            adsk.doEvents()
            sleep(1)
            parent.parentDesign.parentDocument.activate()
            parent.parentDesign.parentDocument.save("pre panel insert")
            sleep(1)
            adsk.doEvents()
            try:
                occ = parent.occurrences.addByInsert(
                    child.dataFile, 
                    Transformation().fusion_matrix3d(), 
                    True
                )
            except RuntimeError:
                i+=1      

        return occ
class JointOrigin:
    @staticmethod
    def find(name, location):
        return location.jointOrigins.itemByName(name)
    
    @staticmethod
    def create(name, location: adsk.fusion.Component, origin, zaxis, xaxis, isFlipped=False):
        joi = location.jointOrigins.createInput(
                adsk.fusion.JointGeometry.createByPoint(
                    origin
            ))

        joi.xAxisEntity = xaxis
        joi.zAxisEntity = zaxis
        joi.isFlipped = isFlipped
        jorigin = location.jointOrigins.add(
            joi
        )
        jorigin.name = name
        return jorigin

    @staticmethod
    def get_or_create(name, location, origin, zaxis, xaxis, isFlipped=False):
        jo = JointOrigin.find(name, location)
        if jo:
            return jo
        return JointOrigin.create(name, location, origin, zaxis, xaxis, isFlipped)


class Joint:
    @staticmethod
    def find(name, location):
        return location.joints.itemByName(name)
    
    @staticmethod
    def create(name, location: adsk.fusion.Component, o1, o2):
        ji=location.joints.createInput(o1, o2)
        ji.setAsRigidJointMotion()
        #ji.offset = adsk.core.ValueInput.createByObject(off.fusion_sketch())
        #ji.angle =  adsk.core.ValueInput.createByReal(rott)
        j= location.joints.add(ji)
        j.name = name
        return j

    @staticmethod
    def get_or_create(name, location, o1, o2):
        jo = Joint.find(name, location)
        if jo:
            return jo
        return Joint.create(name, location, o1, o2)

    @staticmethod
    def modify(j: adsk.fusion.Joint, **kwargs):
        parms = Parameters.get_created_by(j, j.parentComponent.modelParameters)
        for p in parms:
            for key, value in kwargs.items():
                if key in p.role.lower():
                    p.expression = value
                    break
        return j
        

class Loft:
    @staticmethod
    def find(name, location: adsk.fusion.Component):
        return location.features.loftFeatures.itemByName(name)
    
    @staticmethod
    def create(name, location: adsk.fusion.Component, profiles: List[adsk.fusion.Profile]):
        li = location.features.loftFeatures.createInput(
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        for p in profiles:
            li.loftSections.add(p)
        li.isSolid=False
        li.isTangentEdgesMerged=False
        loft = location.features.loftFeatures.add(li)
        loft.name = name
        return name

    @staticmethod
    def get_or_create(name, location: adsk.fusion.Component, profiles: List[adsk.fusion.Profile]):
        lo = Loft.find(name, location)
        if not lo:
            lo = Loft.create(name, location, profiles)
        return lo

    