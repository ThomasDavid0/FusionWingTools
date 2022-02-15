import adsk.core, adsk.fusion, adsk.cam, traceback
import os, sys
import pkg_resources
from .install_requirements import pip_install, setup_install
from json import load

pip_install(["numpy", "pandas", "scipy"])

setup_install([
    "C://Users//td6834//AppData//Roaming//Autodesk//Autodesk Fusion 360//API//Scripts//geometry", 
    "C://Users//td6834//AppData//Roaming//Autodesk//Autodesk Fusion 360//API//Scripts//AircrafDesign"
    ])


from acdesign.aircraft import Plane


from .wingtool import tag_methods
tag_methods()
from .wingtool.fusion_tools import create_document
def parse_plane(acjson):
    with open(acjson, "r") as f:
        data = load(f)
    data["panels"][0]["dihedral"] = 10.0
    data["panels"][0]["otbd"]["incidence"] = 10.0

    return Plane.create(**data)


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        plane = parse_plane("C://Users//td6834//AppData//Roaming//Autodesk//Autodesk Fusion 360//API//Scripts//WingTool//aircraft.json")
        
        #doc = create_document("test_plane")
        doc = app.activeDocument
        plane.create_fusion(doc)


        ui.activeSelections.add(plane.component)
        ui.commandDefinitions.itemById('FindInWindow').execute()
        
        pass
        
        

    except:
        if ui:
            ui.messageBox('Failed://n{}'.format(traceback.format_exc()))