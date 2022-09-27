import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject, TankRobotPhysicalObject
from EnvironmentDavid.babylon import BABYLON_LiveBackend
from scioi_py_core.core.obstacles import BabylonObstacle, SimpleXYZRObstacle
from EnvironmentDavid.mazes import maze_coop2
import time

# mapping for the controller to make input somewhat realistic
mapping_front_back = 0.65
mapping_turn = 9


class EnvironmentDavid_thisExample(EnvironmentDavid):
    agent1: TankRobotSimObject
    Obstacle1: BabylonObstacle
    agent2: TankRobotSimObject

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.agent1 = None
        self.agent2 = None
        # self.obstacle1 = None

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

        # self.babylon_env.wallsFromList(maze_coop2)
        self.babylon_env.add_simulated_agent(self.agent1)
        self.babylon_env.start_babylon()


def main():
    env = EnvironmentDavid_thisExample(Ts=0.04)
    agent1 = TankRobotSimObject(name='Agent 1', world=env.world)
    obstacle1 = BabylonObstacle(length=0.1, width=0.1, height=0.1, position=[0, 0, 0], world=env.world, babylon_env = env.babylon_env)
    # obstacle1 = SimpleXYZRObstacle(length=0.1, width=0.1, height=0.1, position=[0, 0, 0], world=env.world)


    env.agent1 = agent1
    env.obstacle1 = obstacle1


    # env.init(calltree=False)
    env.init()

    env.start()


if __name__ == '__main__':
    main()
