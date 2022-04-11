import adsk.core, adsk.fusion, adsk.cam, traceback
import os, sys
import pkg_resources
from .install_requirements import pip_install, setup_install
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


from .wingtool import tag_methods
tag_methods()



def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

               
        plane = ConventionalPlane.parse_json(Path(__file__).parent / "examples/BUDDI_tilt.json")
        
        proj = Project.get_or_create("test6")
#
        fplane = FusionPlane(plane, proj)

        pass
        
    except:
        if ui:
            ui.messageBox('Failed://n{}'.format(traceback.format_exc()))

