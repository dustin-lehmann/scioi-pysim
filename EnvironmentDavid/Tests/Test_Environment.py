import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject, TankRobotPhysicalObject
from EnvironmentDavid.babylon import BABYLON_LiveBackend
from EnvironmentDavid.baseline.baseline_environment import BayblonVisualization
from EnvironmentDavid.mazes import maze_coop2
import time

# mapping for the controller to make input somewhat realistic
mapping_front_back = 0.65
mapping_turn = 9


class EnvironmentDavid_thisExample(EnvironmentDavid):
    babylon_env: BayblonVisualization
    agent1: TankRobotSimObject
    agent2: TankRobotSimObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.agent1 = None
        self.agent2 = None
        self.babylon_env = None

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)

        if self.joystick.connected:
            # agent1 = self.world.getObjectsByName(name='Agent 1')[0]
            # agent1.dynamics.input = [self.joystick.axis[0], self.joystick.axis[1]]
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
        print("Init")

        # Init of Simulation Environment
        self.babylon_env = BayblonVisualization()
        self.babylon_env.wallsFromList(maze_coop2)
        # self.babylon_env.add_real_agent(self.agent1, self.agent2)
        self.babylon_env.add_simulated_agent(self.agent1)
        self.babylon_env.start_babylon()


def main():
    env = EnvironmentDavid_thisExample(Ts=0.04)
    # todo: sim objects haben keine abmaße? ->added
    agent1 = TankRobotSimObject(name='Agent 1', world=env.world)
    env.agent1 = agent1



    env.init(calltree=False)

    env.start()


if __name__ == '__main__':
    main()
