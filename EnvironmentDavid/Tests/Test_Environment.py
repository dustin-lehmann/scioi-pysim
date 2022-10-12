import scioi_py_core.core as core
from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject, TankRobotPhysicalObject
from EnvironmentDavid.babylon import BABYLON_LiveBackend
from scioi_py_core.core.obstacles import SimpleXYZRObstacle, Obstacle, TestbedFloor, FloorTile, Wall
from EnvironmentDavid.mazes import maze_coop2
import time

# mapping for the controller to make input somewhat realistic
controller_mapping_front_back = 0.65
controller_mapping_turn = 9


class EnvironmentDavid_thisExample(EnvironmentDavid):
    agent1: TankRobotSimObject
    Obstacle1: SimpleXYZRObstacle
    agent2: TankRobotSimObject

    def __init__(self, visualization=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visualization = visualization
        self.agent1 = None
        self.agent2 = None
        # self.obstacle1 = None

    def action_controller(self, *args, **kwargs):
        super().action_controller(*args, **kwargs)

        if self.joystick.connected:
            self.agent1.dynamics.input = [-self.joystick.axis[1] * controller_mapping_front_back,
                                          -self.joystick.axis[2] * controller_mapping_turn]

    def action_visualization(self, *args, **kwargs):
        super().action_visualization(*args, **kwargs)

        sample = self.babylon_env.generate_sample()  # todo: move to the init where this function should be added
        self.babylon_env.webapp.sendSample(sample)
        time.sleep(0.001)

    def _init(self, *args, **kwargs):
        super()._init(*args, **kwargs)

        if self.visualization == 'babylon':
            self.update_babylon_objects()

        self.babylon_env.start_babylon()

    def update_babylon_objects(self):
        # add all objects from the world to babylon
        for obj in self.babylon_env.babylon_objects_dict['existing']:
            # compare objects from last sample with objects in the world right now -> missing ones deleted
            if obj not in self.world.objects:
                self.babylon_env.babylon_objects_dict['deleted'][obj.name]

        for obj in self.world.objects:
            # compare objects in world right now with objects in the last sample -> missing ones added
            if obj not in self.babylon_env.babylon_objects_dict['existing']:
                # object has newly been added -> needs to be added to bayblon as well!
                self.babylon_env.babylon_objects_dict['added'][obj.name]

        for obj in self.world.objects:
            self.babylon_env.babylon_objects_dict['existing'][obj.name] = obj


def main():
    env = EnvironmentDavid_thisExample(Ts=0.04, visualization='babylon', texture_settings='standard_textures')
    # floor = BabylonSimpleFloor(env)
    agent1 = TankRobotSimObject(name='Agent 1', world=env.world)
    env.agent1 = agent1

    obstacle1 = SimpleXYZRObstacle(name='Obstacle 1', length=0.1, width=0.1, height=0.1, position=[0, 0, 0],
                                   world=env.world)
    obstacle2 = SimpleXYZRObstacle(name='Obstacle 2', length=0.1, width=0.1, height=0.1, position=[0.5, 0, 0],
                                   world=env.world)
    obstacle3 = SimpleXYZRObstacle(name='Obstacle 3', length=0.1, width=0.1, height=0.1, position=[1, 0, 0],
                                   world=env.world)

    wall1 = Wall(name='Wall 1', position=[2.5, 1.6, 0.0], lenght=2, height=0.1, world=env.world)

    testbed_floor = TestbedFloor(env=env, world=env.world)  # todo: only pass env and then go from there by passing the world

    env.init()

    env.start()


if __name__ == '__main__':
    main()
