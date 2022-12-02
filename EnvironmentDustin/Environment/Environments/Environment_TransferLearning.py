import matplotlib.pyplot as plt
import numpy as np

from EnvironmentDustin.Environment.Environments.environment_base import EnvironmentBase
from EnvironmentDustin.Environment.EnvironmentTWIPR_objects import TankRobotSimObject, TWIPR_Agent, TWIPR_DynamicAgent, TWIPR_ILC_Agent, standard_reference_trajectory
from scioi_py_core.core.obstacles import CuboidObstacle_3D
from scioi_py_core.objects.world import floor
import scioi_py_core.core as core
from scioi_py_core.utils.joystick import joystick


class Environment_TransferLearning(EnvironmentBase):
    agent1: TWIPR_Agent
    agent2: TWIPR_Agent
    obstacle1: CuboidObstacle_3D

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agent1 = TWIPR_Agent(world=self.world, agent_id=1, speed_control=True)
        self.agent2 = TWIPR_Agent(world=self.world, agent_id=2, speed_control=True)

        self.agent1.setPosition(y=-0.4)
        self.agent2.setPosition(y=0.4)

        fl1 = floor.generateTileFloor(self.world, tiles=[6, 1], tile_size=0.4)

        fl2 = floor.generateTileFloor(self.world, tiles=[6, 1], tile_size=0.4)

        fl1.setPosition(y=-0.4)
        fl2.setPosition(y=0.4)


    def action_input(self, *args, **kwargs):
        super().action_input(*args, **kwargs)

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)
        # self.agent2.input = [-2 * self.joystick.axis[1], -4 * self.joystick.axis[2]]


def main():
    env = Environment_TransferLearning(visualization='babylon', webapp_config={'title': 'Transfer Learning'})
    env.init()
    env.start()
    ...


if __name__ == '__main__':
    main()
