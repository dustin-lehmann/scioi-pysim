import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject, TankRobotPhysicalObject
from EnvironmentDavid.babylon import BABYLON_LiveBackend
from EnvironmentDavid.baseline.baseline_environment import BayblonVisualization
from scioi_py_core.core.obstacles import  SimpleXYZRObstacle
from EnvironmentDavid.mazes import maze_coop2
import time

# mapping for the controller to make input somewhat realistic
mapping_front_back = 0.65
mapping_turn = 9


class EnvironmentDavid_thisExample(EnvironmentDavid):
    babylon_env: BayblonVisualization
    agent1: TankRobotSimObject
    Obstacle1: SimpleXYZRObstacle
    agent2: TankRobotSimObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.agent1 = None
        self.agent2 = None
        self.obstacle1 = None
        self.babylon_env = None

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)

        if self.joystick.connected:
            self.agent1.dynamics.input = [-self.joystick.axis[1] * mapping_front_back,
                                          -self.joystick.axis[2] * mapping_turn]

    def action_visualization(self, *args, **kwargs):
        super().action_visualization(*args, **kwargs)
        super().action_visualization(*args, **kwargs)

        sample = self.babylon_env.generateSample()
        self.babylon_env.webapp.sendSample(sample)
        time.sleep(0.001)

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)

        # Init of Simulation Environment
        self.babylon_env = BayblonVisualization()
        self.babylon_env.start_babylon()


def main():
    env = EnvironmentDavid_thisExample(Ts=0.04)

    obstacle1 = SimpleXYZRObstacle(length = 100, width=100, height= 100, position=0, world = env.world)

    # todo: calltree param not working as soon as Obstacle is created instead of robot
    # env.init(calltree=False)
    # todo: quickfix
    env.init()

    env.start()


if __name__ == '__main__':
    main()
