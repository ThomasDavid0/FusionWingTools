

from acdesign.aircraft import Plane, Panel, Rib
from .fusion_tools import Component, Document, Sketch, Folder, Parameters, Occurence, Spline, Line, JointOrigin, Joint
from geometry import Points, Point, Quaternion, Transformation
import adsk.core, adsk.fusion
from time import sleep
from typing import List, Tuple, Dict
import numpy as np
from .fusion_panel import PlacedPanel

app = adsk.core.Application.get()


class FusionPlane:
    def __init__(self, plane: Plane, project):
        self.project = project
        self.plane = plane
        self.doc = Document.get_or_create("OML_Global", self.project.rootFolder)
        
        #panels = [PlacedPanel.find(p.comment) for p in uparms if "paneldef_" in p.name]
        self.panels = [PlacedPanel(p, self.doc) for p in self.plane.panels]

    
    