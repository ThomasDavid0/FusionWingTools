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


from acdesign.aircraft import Plane


from .wingtool import tag_methods
tag_methods()
from .wingtool.fusion_tools import create_document, create_project, get_item

def parse_plane(acjson):
    with open(acjson, "r") as f:
        data = load(f)
    #data["panels"][0]["dihedral"] = 10.0
   # data["panels"][0]["otbd"]["incidence"] = 5.0
   # data["panels"][0]["otbd"]["airfoil"] = "dae21-il"
    #
    #data["panels"][0]["inbd"]["chord"] = 300.0
   # data["panels"][0]["inbd"]["airfoil"] = "defcnd1-il"
    return Plane.create(**data)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        plane = parse_plane(Path(__file__).parent / "aircraft.json")
        
        #proj = create_project("test_plane")
        proj = get_item("test_plane", app.data.dataProjects)
        #doc = app.activeDocument
        plane.create_fusion(proj)


        #ui.activeSelections.add(plane.component)
        #ui.commandDefinitions.itemById('FindInWindow').execute()
        
    except:
        if ui:
            ui.messageBox('Failed://n{}'.format(traceback.format_exc()))