

from acdesign.aircraft import Plane, Panel, Rib
from .fusion_tools import Component, Document, Sketch, Folder, Parameters, Occurence, Spline, Line, JointOrigin, Joint
from geometry import Points, Point, Quaternion, Transformation
import adsk.core, adsk.fusion
from time import sleep
from typing import List, Tuple, Dict
import numpy as np
from .fusion_panel import create_or_update_panel

app = adsk.core.Application.get()



class PlacedPanel:
    def __init__(self, name, doc: adsk.core.Document, joint: adsk.fusion.Joint):
        self.name = name
        self.doc = doc
        self.joint = joint
    
    @staticmethod
    def find(name, parent: adsk.core.Document):
        return PlacedPanel(
            name,
            Document.find(f"panel_{name}", parent.dataFile.parentFolder.dataFiles),
            Joint.find(f"panel_{name}", parent.design.rootComponent)
        )

    @staticmethod
    def create_or_update(panel: Panel, parent: adsk.core.Document):
        
        parms = {}
        for direc in list("xyz"):
            parms[direc] = Parameters.set_or_create(
                parent.design.userParameters, 
                f"panel_{panel.name}_{direc}",
                getattr(panel, direc) / 10,
                "mm",
                panel.name,
            )

        parms["angle"] = Parameters.set_or_create(
            parent.design.userParameters, 
            f"panel_{panel.name}_dihedral",
            panel.dihedral,
            "deg",
            panel.name,
        )
        
        dihedral = JointOrigin.get_or_create(
            "dihedral",
            parent.design.rootComponent, 
            parent.design.rootComponent.originConstructionPoint, 
            parent.design.rootComponent.xConstructionAxis, 
            parent.design.rootComponent.yConstructionAxis
        )

        doc = Document.get_or_create(panel.name, parent.dataFile.parentFolder)
        
        create_or_update_panel(doc, panel)
        for ref in parent.documentReferences:
            ref.getLatestVersion()
               
        doc.save("panel created or updated")
            
        i=0
        occ=None
        while not occ:
            occ = Occurence.find_by_component(panel.name, parent.design.rootComponent)
            if not occ is None or i > 5:
                break
            doc.activate()
            adsk.doEvents()
            sleep(1)
            parent.activate()
            parent.save("pre panel insert")
            sleep(1)
            adsk.doEvents()
            try:
                occ = parent.design.rootComponent.occurrences.addByInsert(doc.dataFile, Transformation().fusion_matrix3d(), True)
            except RuntimeError:
                i+=1

        if occ:
            joint = Joint.modify(
                Joint.get_or_create(
                    panel.name, 
                    parent.design.rootComponent,
                    JointOrigin.find("dihedral", occ.component).createForAssemblyContext(occ), # the dihedral joint
                    dihedral,
                ),
                x=parms["z"].name,
                y=parms["y"].name,
                z=parms["x"].name,
                angle=f"-{parms['angle'].name}" 
            )
        else: 
            joint=None     
        doc.close(True)   
        return PlacedPanel(panel.name, doc, joint)



def create_plane(project: adsk.core.DataProject, plane: Plane):
    doc = Document.get_or_create("OML_Global", project.rootFolder)
    
    uparms = Parameters.get_dict(doc.design.userParameters)
    #panels = [PlacedPanel.find(p.comment) for p in uparms if "paneldef_" in p.name]
    panels = [PlacedPanel.create_or_update(p, doc) for p in plane.panels]

    
    