import adsk.core, adsk.fusion, adsk.cam, traceback
import os, sys
import pkg_resources
from wingtool.install_requirements import pip_install, setup_install
from json import load
from pathlib import Path


pip_install(["numpy", "pandas", "scipy"])

setup_install([
    Path(__file__).parent / "geometry", 
    Path(__file__).parent / "AircrafDesign"
    ])


from acdesign.aircraft.plane import ConventionalPlane
from .wingtool.fusion_tools import Document, Parameters, JointOrigin, Project
from .wingtool.fusion_aircraft import FusionPlane
from .wingtool.fusion_panel import FusionPanel


from .wingtool import tag_methods
tag_methods()



def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        infile = Path(__file__).parent / "examples/f3a.json"# "examples/BUDDI_tilt.json"#  # 
        outdes = "Placebo"#"BUDDI_V3"#
        plane = ConventionalPlane.parse_json(infile)
        proj = Project.get_or_create(outdes)
        #fpanel = FusionPanel(app.activeDocument)

        fplane = FusionPlane(plane, proj)

        pass
        
    except:
        if ui:
            ui.messageBox('Failed://n{}'.format(traceback.format_exc()))

