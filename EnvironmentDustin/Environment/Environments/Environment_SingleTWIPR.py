import random

from EnvironmentDustin.Environment.Environments.environment_base import EnvironmentBase
from EnvironmentDustin.Environment.EnvironmentTWIPR_objects import TankRobotSimObject, TWIPR_Agent
from scioi_py_core.core.obstacles import CuboidObstacle_3D


class Environment_SingleTWIPR(EnvironmentBase):
    agent1: TWIPR_Agent
    obstacle1: CuboidObstacle_3D

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TWIPR_Agent(agent_id=1, name='Agent 1', world=self.world)
        self.obstacle1 = CuboidObstacle_3D(name='Obstacle 1', world=self.world, position=[1, 0, 0], size_x=0.25,
                                           size_y=0.25, size_z=0.25)
        # self.obstacle2 = CuboidObstacle_3D(name='Obstacle 2', world=self.world, position=[0, 1, 0], size_x=0.25,
        #                                    size_y=0.25, size_z=0.25)
        # self.obstacle3 = CuboidObstacle_3D(name='Obstacle 3', world=self.world, position=[0, 0, 1], size_x=0.25,
        #                                    size_y=0.25, size_z=0.25)

    def action_input(self, *args, **kwargs):
        super().action_input(*args, **kwargs)
