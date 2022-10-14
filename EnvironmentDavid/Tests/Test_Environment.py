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
            # initialize world for babylon
            self.update_babylon_objects()

        self.babylon_env.start_babylon()

    def update_babylon_objects(self):
        """
        update the babylon object dictionary with:

        :return: nothinh
        """
        sample = self.world.create_world_sample()
        self.babylon_env.babylon_objects_dict = sample

        # keys = self.world.objects.keys()
        # # used to update existing objects
        # shared_items = {k: self.babylon_env.babylon_objects_dict['existing'][k] for k in
        #                 self.babylon_env.babylon_objects_dict['existing'] if
        #                 k in self.world.objects and self.babylon_env.babylon_objects_dict['existing'][k] ==
        #                 self.world.objects[k]}
        #
        # added_items = {k: self.world.objects[k] for k in
        #                set(self.world.objects) - set(self.babylon_env.babylon_objects_dict['existing'])}
        #
        # deleted_items = {k: self.babylon_env.babylon_objects_dict['existing'][k] for k in
        #                  set(self.babylon_env.babylon_objects_dict['existing']) - set(self.world.objects)}
        #
        # self.babylon_env.babylon_objects_dict['existing'] = shared_items
        # self.babylon_env.babylon_objects_dict['added'] = added_items
        # self.babylon_env.babylon_objects_dict['deleted'] = deleted_items
        # print('end')


def main():
    env = EnvironmentDavid_thisExample(Ts=0.04, visualization='babylon', texture_settings='standard_textures')

    agent1 = TankRobotSimObject(name='Agent 1', world=env.world)
    env.agent1 = agent1

    obstacle1 = SimpleXYZRObstacle(name='Obstacle 1', length=0.1, width=0.1, height=0.1, position=[0, 0, 0],
                                   world=env.world)
    obstacle2 = SimpleXYZRObstacle(name='Obstacle 2', length=0.1, width=0.1, height=0.1, position=[0.5, 0, 0],
                                   world=env.world)
    obstacle3 = SimpleXYZRObstacle(name='Obstacle 3', length=0.1, width=0.1, height=0.1, position=[1, 0, 0],
                                   world=env.world)

    wall1 = Wall(name='Wall 1', position=[2.5, 1.6, 0.0], lenght=2, height=0.1, world=env.world)

    testbed_floor = TestbedFloor(env=env,
                                 world=env.world)  # todo: only pass env and then go from there by passing the world

    env.init()

    env.start()


if __name__ == '__main__':
    main()
