
from geometry import Point, Points, Transformation
from acdesign.aircraft import Plane, Panel, Rib

from .create_geom import *
from .create_ac import *
from .mappers import *

def tag_methods():
    
    Transformation.fusion_matrix3d = create_matrix3d
    Point.fusion_sketch = create_sketch_point
    Points.fusion_sketch = create_sketch_points
   
   
    Rib.create_fusion = create_rib
    Panel.create_fusion = create_panel
    Plane.create_fusion = create_plane

   
    Rib.map_fusion = map_fusion_rib
    Panel.map_fusion = map_fusion_panel
    Plane.map_fusion = map_fusion_plane