import random

from EnvironmentDustin.Environment.Environments.environment_base import EnvironmentBase
from EnvironmentDustin.Environment.EnvironmentTWIPR_objects import TankRobotSimObject, TWIPR_Agent, TWIPR_DynamicAgent
from scioi_py_core.core.obstacles import CuboidObstacle_3D


class Environment_SingleTWIPR(EnvironmentBase):
    agent1: TWIPR_DynamicAgent
    obstacle1: CuboidObstacle_3D

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TWIPR_DynamicAgent(agent_id=1, name='Agent 1', world=self.world, speed_control=True)

    def action_input(self, *args, **kwargs):
        super().action_input(*args, **kwargs)

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)
        self.agent1.input = [-2*self.joystick.axis[1], -4*self.joystick.axis[2]]
        pass



