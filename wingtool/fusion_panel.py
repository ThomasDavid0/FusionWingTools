
from acdesign.aircraft import Plane, Panel, Rib
from .fusion_tools import Parameters, JointOrigin, Joint, Document, Loft, Occurence
from .fusion_rib import FusionRib
from geometry import Points, Point, Quaternion, Transformation
import adsk.core, adsk.fusion
from time import sleep
from typing import List, Tuple, Dict
import numpy as np


app = adsk.core.Application.get()


panel_fusion_mapping = {
    "length":                    lambda p : (0.1 * p.semispan,                             "mm",  ""),
    "desired_root_chord":        lambda p : (0.1 * p.inbd.chord,                           "mm",  ""),
    "desired_tip_chord":         lambda p : (0.1 * p.otbd.chord,                           "mm",  ""),
    "root_incidence":            lambda p : (p.inbd.incidence + p.incidence,               "rad", ""),
    "tip_incidence":             lambda p : (p.otbd.incidence + p.incidence,               "rad", ""),
    "le_sweep":                  lambda p : (0.1 * p.le_sweep_distance,                    "mm",  ""),
    "mean_chord_prop":           lambda p : (0.25,                                         "",    ""),
    "desired_root_section":      lambda p : (0,                                            "",    p.inbd.name),
    "desired_tip_section":       lambda p : (0,                                            "",    p.otbd.name),
    "desired_root_te_thickness": lambda p : (0.1 * p.inbd.te_thickness,                    "mm",  ""),
    "desired_tip_te_thickness":  lambda p : (0.1 * p.otbd.te_thickness,                    "mm",  ""),
}


def dump_panel_parameters(p: Panel, target: adsk.fusion.UserParameters) -> Dict[str, adsk.fusion.Parameter]:
    return {key: Parameters.set_or_create(target, key, *value(p)) for key, value in panel_fusion_mapping.items()}


def parse_panel_parms(doc) -> Panel:
    uparms = Parameters.get_dict(doc.design.userParameters)
    return Panel.create(
        name=doc.name.split(" ")[0],
        acpos=Point.zeros().to_dict(),
        dihedral=0.0,
        incidence=0.0,
        inbd={
            "airfoil":uparms["desired_root_section"].comment, 
            "chord":uparms["desired_root_chord"].value * 10, 
            "te_thickness":uparms["desired_root_te_thickness"].value * 10
        },
        otbd={
            "airfoil":uparms["desired_tip_section"].comment, 
            "chord":uparms["desired_tip_chord"].value * 10, 
            "te_thickness":uparms["desired_tip_te_thickness"].value * 10
        },
        sweep=uparms["le_sweep"].value * 10,
        length=uparms["length"].value * 10
    )


class FusionPanel:
    def __init__(self, doc: adsk.core.Document):
        self.doc = doc
        
        self.comp = doc.design.rootComponent
        self.panel = Panel.parse_fusion_parms(doc)
        self.i_jo = JointOrigin.get_or_create(
            "incidence",
            self.comp, 
            self.comp.originConstructionPoint, 
            self.comp.yConstructionAxis, 
            self.comp.xConstructionAxis
        )
        self.d_jo = JointOrigin.get_or_create(
            "dihedral",
            self.comp, 
            self.comp.originConstructionPoint, 
            self.comp.xConstructionAxis, 
            self.comp.yConstructionAxis,
            True
        )
        self.root=FusionRib(doc, "root")
        self.tip=FusionRib(doc, "tip")

        self.rootjoint = Joint.modify(
            Joint.get_or_create(
                "root", 
                self.comp,
                adsk.fusion.JointGeometry.createByPoint(self.root.ocp), 
                self.i_jo
            ), 
            angle=Parameters.find("root_incidence", self.doc.design.userParameters).name
        )

        self.tipjoint = Joint.modify(
            Joint.get_or_create(
                "tip", 
                self.comp,
                adsk.fusion.JointGeometry.createByPoint(self.tip.ocp), 
                self.i_jo
            ), 
            x=Parameters.find("le_sweep", self.doc.design.userParameters).name,
            z=Parameters.find("length", self.doc.design.userParameters).name, 
            angle=Parameters.find("tip_incidence", self.doc.design.userParameters).name
        )
        doc.save("panel updated")


class PlacedPanel(FusionPanel):
    def __init__(self, panel: Panel, parent: adsk.core.Document):
        self.parent = parent
        
        doc = Document.get_or_create(panel.name, parent.dataFile.parentFolder)
        panel.dump_fusion_parms(doc.design.userParameters)
        super().__init__(doc)
        self.panel = panel

        parms = {}
        for direc in list("xyz"):
            parms[direc] = Parameters.set_or_create(
                self.parent.design.userParameters, 
                f"panel_{self.panel.name}_{direc}",
                getattr(self.panel, direc)[0] / 10,
                "mm",
                self.panel.name,
            )

        parms["angle"] = Parameters.set_or_create(
            parent.design.userParameters, 
            f"panel_{self.panel.name}_dihedral",
            self.panel.dihedral,
            "deg",
            self.panel.name,
        )
        
        self.d_jo = JointOrigin.get_or_create(
            "dihedral",
            parent.design.rootComponent, 
            parent.design.rootComponent.originConstructionPoint, 
            parent.design.rootComponent.xConstructionAxis, 
            parent.design.rootComponent.yConstructionAxis
        )

        for ref in parent.documentReferences:
            ref.getLatestVersion()

        self.occ = Occurence.insert_component(parent.design.rootComponent, self.doc)

        if self.occ:
            self.joint = Joint.modify(
                Joint.get_or_create(
                    panel.name, 
                    parent.design.rootComponent,
                    JointOrigin.find("dihedral", self.occ.component).createForAssemblyContext(self.occ), # the dihedral joint
                    self.d_jo,
                ),
                x=parms["y"].name,
                y=parms["z"].name,
                z=parms["x"].name,
                angle=f"-{parms['angle'].name}" 
            )
        else: 
            self.joint=None     
        #self.doc.close(True)   
        


    
    @staticmethod
    def find(name, parent):
        return PlacedPanel(
            parent,
            Document.find(f"panel_{name}", parent.dataFile.parentFolder.dataFiles),
            Joint.find(f"panel_{name}", parent.design.rootComponent)
        )


#        self.loft = Loft.get_or_create(
#            "OML", 
#            self.comp, 
#            [
#                Sketch.find("base_profile", self.root).createForAssemblyContext()
#            ]
#        )













