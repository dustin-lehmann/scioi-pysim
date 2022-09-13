import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject, TankRobotPhysicalObject
from EnvironmentDavid.babylon import BABYLON_LiveBackend
from EnvironmentDavid.baseline.baseline_environment import BayblonVisualization
from EnvironmentDavid.mazes import maze_coop2
import time


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
            self.agent1.dynamics.input = [self.joystick.axis[0], self.joystick.axis[1]]

    # def world(self, *args, **kwargs):
    #     super().world(*args, **kwargs)
    #
    #     #create sample data

    def action_visualization(self, *args, **kwargs):
        super().action_visualization(*args, **kwargs)
        super().action_visualization(*args, **kwargs)

        sample = self.babylon_env.generateSample()
        self.babylon_env.webapp.sendSample(sample)
        time.sleep(0.001)
        "change position of robots with update function"

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)
        print("Init")

        # Init of Simulation Environment
        self.babylon_env = BayblonVisualization()
        self.babylon_env.wallsFromList(maze_coop2)
        # self.babylon_env.add_real_agent(self.agent1, self.agent2)
        self.babylon_env.add_simulated_agent(self.agent1, self.agent2)
        self.babylon_env.start_babylon()


def main():
    env = EnvironmentDavid_thisExample(Ts=1)
    # todo: sim objects haben keine abmaße? ->added
    agent1 = TankRobotSimObject(name='Agent 1', world=env.world)
    agent2 = TankRobotSimObject(name='Agent 2', world=env.world)

    # agent1 = TankRobotPhysicalObject()
    # agent2 = TankRobotPhysicalObject()

    env.agent1 = agent1
    env.agent2 = agent2

    # agent1.dynamics.input = [1, 0]

    def print_agent1_state(*args, **kwargs):
        print(f"Agent 1 State: {agent1.dynamics.state}")


    core.scheduling.Action(name="Print Agent", function=print_agent1_state, parent=env.scheduling.actions['output'])

    env.init(calltree=False)

    env.start()


if __name__ == '__main__':
    main()
