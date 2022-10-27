from EnvironmentDustin.Environment.Environments.environment_base import EnvironmentTWIPR
from EnvironmentDustin.Environment.objects.EnvironmentTWIPR_objects import TankRobotSimObject
from scioi_py_core.core.obstacles import CuboidObstacle_3D


class Environment_SingleTWIPR(EnvironmentTWIPR):
    agent1: TankRobotSimObject
    obstacle1: CuboidObstacle_3D

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TankRobotSimObject(name='Agent 1', world=self.world)
        self.obstacle1 = CuboidObstacle_3D(name='Obstacle', world=self.world, position=[1, 1, 1], size_x=1, size_y=0.2, size_z=0.2)
