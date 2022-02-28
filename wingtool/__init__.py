
from geometry import Point, Points, Transformation, Quaternion
from acdesign.aircraft import Plane, Panel, Rib

from .create_geom import *
from .create_ac import *
from .mappers import *

def tag_methods():
    
    Transformation.fusion_matrix3d = create_matrix3d
    Point.fusion_sketch = create_sketch_point
    Points.fusion_sketch = create_sketch_points

    Transformation.from_matrix3d = parse_matrix3d
      