
from geometry import Point, Points, Transformation, Quaternion
from acdesign.aircraft import Plane, Panel, Rib

from .create_geom import *
from .fusion_rib import create_or_update_rib
from .fusion_panel import create_or_update_panel, parse_fusion_panel_parms
from .mappers import *

def tag_methods():
    
    Transformation.fusion_matrix3d = create_matrix3d
    Point.fusion_sketch = create_sketch_point
    Points.fusion_sketch = create_sketch_points

    Transformation.from_matrix3d = parse_matrix3d
    
    Rib.dump_fusion = create_or_update_rib

    Panel.parse_fusion = parse_fusion_panel_parms
    Panel.dump_fusion = create_or_update_panel

