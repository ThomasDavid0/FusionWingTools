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




def run(context):
    ui = None
    try:
        
        from acdesign.aircraft import Plane
        from .creators import create_plane
        app = adsk.core.Application.get()
        ui  = app.userInterface

        
        with open("C://Users//td6834//AppData//Roaming//Autodesk//Autodesk Fusion 360//API//Scripts//AircrafDesign//tests//data//aircraft.json", "r") as f:
            plane = Plane.create(**load(f))


        doc = create_plane(plane)        

#   
        #sketch = create_rib(component, plane.panels[0].inbd)
        
        

    except:
        if ui:
            ui.messageBox('Failed://n{}'.format(traceback.format_exc()))