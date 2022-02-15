import adsk.core, adsk.fusion, adsk.cam, traceback

from geometry import Transformation, Point, Points
from itertools import chain
from .fusion_tools import full_obj_collection


def create_matrix3d(self: Transformation):
    matr =  adsk.core.Matrix3D.create()
    matd = self.to_matrix().T.tolist()

    if matr.setWithArray(list(chain(*matd))):
        return matr
    else:
        raise Exception("couldnt set the transformation")


def create_sketch_point(self: Point):
    return adsk.core.Point3D.create(*self.to_list())


def create_sketch_points(self: Points):
    return full_obj_collection([create_sketch_point(p) for p in self])


