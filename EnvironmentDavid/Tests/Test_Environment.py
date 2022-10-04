import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject, TankRobotPhysicalObject
from EnvironmentDavid.babylon import BABYLON_LiveBackend
from scioi_py_core.core.obstacles import SimpleObstacle, SimpleXYZRObstacle, Obstacle
from EnvironmentDavid.mazes import maze_coop2
import time

# mapping for the controller to make input somewhat realistic
mapping_front_back = 0.65
mapping_turn = 9


class EnvironmentDavid_thisExample(EnvironmentDavid):
    agent1: TankRobotSimObject
    Obstacle1: SimpleObstacle
    agent2: TankRobotSimObject

    def __init__(self, visualization=None, visualization_settings=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visualization = visualization
        self.visualization_settings = visualization_settings
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

        sample = self.babylon_env.generateSample()  # todo: move to the init where this function should be added
        self.babylon_env.webapp.sendSample(sample)
        time.sleep(0.001)

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)

        if self.visualization == 'babylon':
            # add all objects from the world to babylon
            for obj in self.world.getObjectsByType(Obstacle):  # todo: change to one single function_call? -> depends on how the robvots are used -> should they be added to a list with generate sample?
                self.babylon_env.add_object_to_babylon(obj)

            for obj in self.world.getObjectsByType(TankRobotSimObject):
                self.babylon_env.add_object_to_babylon(obj)

        #
        self.babylon_env.start_babylon()


def main():
    env = EnvironmentDavid_thisExample(Ts=0.04, visualization='babylon', visualization_settings='fancy.json')
    # floor = BabylonSimpleFloor(env)
    agent1 = TankRobotSimObject(name='Agent 1', world=env.world)


    obstacle1 = SimpleXYZRObstacle(name='Obstacle 1', length=0.1, width=0.1, height=0.1, position=[0, 0, 0],
                                   world=env.world)
    obstacle2 = SimpleXYZRObstacle(name='Obstacle 2', length=0.1, width=0.1, height=0.1, position=[0.5, 0, 0],
                                   world=env.world)
    obstacle3 = SimpleXYZRObstacle(name='Obstacle 3', length=0.1, width=0.1, height=0.1, position=[1, 0, 0],
                                   world=env.world)

    env.init()

    env.start()


if __name__ == '__main__':
    main()
