import asyncio
import time

from EnvironmentDavid.babylon import BABYLON_LiveBackend
from scioi_py_core.core.objects import VisulizationEnvironment, ObstacleBox, BabylonRobot, AreaBox, Door, Switch, Goal
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotPhysicalObject
import threading


# class TestbedVisualizationEnvironment(VisulizationEnvironment):
#     size_x = 5094
#     size_y = 3679
#     tiles_x = 18
#     tiles_y = 13
#     base_height = 150
#     wall_thickness = 10
#
#     robots = 1
#     robot_length = 152
#     robot_width = 120
#     robot_height = 50
#
#     def __init__(self):
#         super().__init__()
#         self.robots = {
#             'robot_01': Robot(self.robot_length, self.robot_width, self.robot_height)
#         }
#         self.areas = {}

#
# class BaselineVisulizationEnvironment_2(VisulizationEnvironment):
#     size_x = 5094
#     size_y = 3679
#     tiles_x = 18
#     tiles_y = 13
#     base_height = 150
#     wall_thickness = 10
#
#     robot_length = 170
#     robot_width = 140
#     robot_height = 50
#
#     def __init__(self):
#         super().__init__()
#         self.robots = {
#             'robot_01': Robot(1, self.robot_length, self.robot_width, self.robot_height, environment=self),
#             'robot_02': Robot(2, self.robot_length, self.robot_width, self.robot_height, environment=self)
#         }
#         self.switches = {
#             'Switch_1': Switch(cell=[2, 9], momentary=False, id=1),
#             'Switch_2': Switch(cell=[15, 9], momentary=False, id=2),
#             'Switch_3': Switch(cell=[0, 0], momentary=False, id=3),
#             'Switch_4': Switch(cell=[17, 0], momentary=False, id=4),
#             # 'Switch_3': Switch(cell=[8, 8], momentary=False, id=4),
#         }
#         door_1 = Door.fromTiles('v', 6, 9, 1, self.tile_size, 10, 0, id=1,
#                                 switches=[self.switches['Switch_1']])
#
#         door_2 = Door.fromTiles('v', 11, 9, 1, self.tile_size, 10, 0, id=2,
#                                 switches=[self.switches['Switch_2']])
#
#         door_3 = Door.fromTiles('h', 8, 2, 1, self.tile_size, 10, 0, id=3,
#                                 switches=[self.switches['Switch_2']])
#
#         door_4 = Door.fromTiles('h', 9, 2, 1, self.tile_size, 10, 0, id=4,
#                                 switches=[self.switches['Switch_2']])
#
#         self.doors = {
#             'Door_1': door_1[0],
#             'Door_2': door_2[0],
#             'Door_3': door_3[0],
#             'Door_4': door_4[0],
#
#         }
#
#         self.goals = {
#             'Goal_1': Goal([8, 0], 'any', self.goal_reached_cb, visible=True),
#             'Goal_2': Goal([9, 0], 'any', self.goal_reached_cb, visible=True),}
#
#     def goal_reached_cb(self, *args, **kwargs):
#         pass


class BayblonVisualization(VisulizationEnvironment):
    """
    this class has all the elements relevant for the babylon visualization of the Testbed
    """
    size_x = 5094
    size_y = 3679
    tiles_x = 18
    tiles_y = 13
    base_height = 150
    wall_thickness = 10
    webapp = None
    robot_list = []

    def __init__(self):

        robot_count = 0
        print('init start')
        super().__init__()
        # for element in args:
        #     print('trying to add robot to tuple')
        #     # self.robots[f'robot{element}']: Robot(element.length, element.width, element.height)
        #     self.robots.append(Robot(element.length, element.width, element.height))

        # self.robots = {
        #     'robot_01': Robot(1, self.robot_length, self.robot_width, self.robot_height, environment=self),
        #     'robot_02': Robot(2, self.robot_length, self.robot_width, self.robot_height, environment=self)
        # }

        # self.switches = {
        #     'Switch_1': Switch(cell=[12, 12], momentary=True, id=1),
        #     'Switch_2': Switch(cell=[12, 8], momentary=False, id=1),
        #     'Switch_3': Switch(cell=[8, 8], momentary=False, id=4),
        # }
        # door_1 = Door.fromTiles('h', 10, 10, 1, self.tile_size, 10, 0, id=1,
        #                         switches=[self.switches['Switch_1'], self.switches['Switch_2']])
        #
        # door_2 = Door.fromTiles('v', 9, 9, 1, self.tile_size, 10, 0, id=4,
        #                         switches=[self.switches['Switch_3']])
        #
        # self.doors = {
        #     'Door_1': door_1[0],
        #     'Door_2': door_2[0],
        # # }
        # #
        # self.goals = {
        #     'Goal_1': Goal([1, 1], 'any', self.goal_reached_cb, visible=True)
        # }

    def add_simulated_agent(self, *args: TankRobotPhysicalObject):
        """
        add another agent to the environment
        """
        #todo: add possibility to add robots via list!
        for element in args:
            self.robots.append(BabylonRobot(element.length, element.width, element.height))

    def start_babylon(self):
        # write all objects into jason
        self.toJson(file="../babylon/objects.json")
        babylon_thread = threading.Thread(target=self._start_webapp)
        babylon_thread.start()
        time.sleep(1) # todo

    def goal_reached_cb(self, *args, **kwargs):
        pass

    def _start_webapp(self):

        asyncio.set_event_loop(asyncio.new_event_loop())
        self.webapp = BABYLON_LiveBackend("../babylon/example_LNDW_simple.html", options={})
        self.webapp.start()
        while True:
            time.sleep(0.1)
