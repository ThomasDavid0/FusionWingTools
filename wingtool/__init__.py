
from geometry import Point, Points, Transformation, Quaternion
from acdesign.aircraft import Plane, Panel, Rib

from .create_geom import *
from .fusion_rib import parse_rib_parms
from .fusion_panel import FusionPanel, parse_panel_parms, dump_panel_parameters
from .mappers import *

def tag_methods():
    
    Transformation.fusion_matrix3d = create_matrix3d
    Point.fusion_sketch = create_sketch_point
    Points.fusion_sketch = create_sketch_points

    Transformation.from_matrix3d = staticmethod(parse_matrix3d)
    
    Rib.parse_parameters = staticmethod(parse_rib_parms)

    Panel.parse_fusion_parms = staticmethod(parse_panel_parms)
    Panel.dump_fusion_parms = dump_panel_parameters


