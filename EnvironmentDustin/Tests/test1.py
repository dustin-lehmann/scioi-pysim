import copy
import json
import math
import time
from math import pi

import numpy as np

from EnvironmentDustin.Environment.Environments.Environment_SingleTWIPR import Environment_SingleTWIPR
from scioi_py_core.objects.world import floor
import scioi_py_core.core as core
import scioi_py_core.utils.orientations as ori_utils


def main():
    env = Environment_SingleTWIPR(visualization='babylon', webapp_config={'title': 'This is a title'})
    fl = floor.generateTileFloor(env.world, tiles=[10, 10], tile_size=0.4)

    # group1 = core.world.WorldObjectGroup(name='Gate', world=env.world, local_space=core.spaces.Space3D())
    # group_object1 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.1, size_y=0.1, size_z=0.2,
    #                                                  position=[0, 0.5, 0.1])
    # group_object2 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.1, size_y=0.1, size_z=0.2,
    #                                                  position=[0, -0.5, 0.1])




    env.init()
    env.start()




# TODO: Implement the translate and rotate functions. Also make some objects fixed so that changing
#  any in their config gives an error

if __name__ == '__main__':
    main()
