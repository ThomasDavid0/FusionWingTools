import adsk.core, adsk.fusion, adsk.cam, traceback
import os, sys
import pkg_resources
from .install_requirements import pip_install, setup_install
from json import load
from pathlib import Path


pip_install(["numpy", "pandas", "scipy"])

setup_install([
    Path(__file__).parent / "_submodules/geometry", 
    Path(__file__).parent / "_submodules/AircrafDesign"
    ])


from acdesign.aircraft import Plane, Rib
from .wingtool.fusion_tools import Document, Parameters, JointOrigin

from .wingtool import tag_methods
tag_methods()


def parse_plane(acjson):
    with open(acjson, "r") as f:
        data = load(f)
    #data["panels"][0]["dihedral"] = 10.0
    #data["panels"][0]["otbd"]["incidence"] = 5.0
    #data["panels"][0]["otbd"]["airfoil"] = "dae21-il"
    ###
    #data["panels"][0]["inbd"]["chord"] = 300.0
    #data["panels"][0]["inbd"]["airfoil"] = "defcnd1-il"
    #data["panels"][0]["inbd"]["incidence"] = -5
    return Plane.create(**data)

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface


        
        plane = parse_plane(Path(__file__).parent / "aircraft.json")
        doc=app.activeDocument
        plane.panels[0].dump_fusion(doc, plane.panels[0])

        
    except:
        if ui:
            ui.messageBox('Failed://n{}'.format(traceback.format_exc()))

