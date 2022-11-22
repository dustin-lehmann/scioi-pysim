import math
import time

import numpy as np

from EnvironmentDustin.Environment.Environments.environment_base import EnvironmentBase
from EnvironmentDustin.Environment.EnvironmentTWIPR_objects import TankRobotSimObject, TWIPR_Agent, TWIPR_DynamicAgent
from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.objects.world import floor
import scioi_py_core.core as core
import scioi_py_core.utils.joystick.joystick as joystick


class Environment_Thesis_Objects(EnvironmentBase):

    def __init__(self,objects:list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obstacle
        if 'obsctale' in objects:
            core.obstacles.CuboidObstacle_3D(world= self.world, size_x=0.2, size_y=0.2, size_z=0.2,position=[0, 0, 0])

        # Floor
        if 'floor' in objects:
            floor.generateTileFloor(self.world, tiles=[5,5], tile_size=0.4)


        # Walls
        if 'wall' in objects:
            core.obstacles.CuboidObstacle_3D(world=self.world, size_x=0.2, size_y=0.01, size_z=0.1, position=[0, 0, 0.05])

        # Group
        if 'group' in objects:

            group1 = core.world.WorldObjectGroup(name='Gate', world=self.world, local_space=core.spaces.Space3D())

            group_object1 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.04, size_z=0.15,
                                                             position=[0, 0.2, 0.075])
            group_object2 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.04, size_z=0.15,
                                                             position=[0, -0.2, 0.075])
            group_object3 = core.obstacles.CuboidObstacle_3D(group=group1, size_x=0.04, size_y=0.44, size_z=0.04,
                                                             position=[0, 0, 0.17])




def main():
    env = Environment_Thesis_Objects(visualization='babylon', webapp_config={'title': 'Playground'},objects = ['group'])
    env.init()
    env.start()


if __name__ == '__main__':
    main()