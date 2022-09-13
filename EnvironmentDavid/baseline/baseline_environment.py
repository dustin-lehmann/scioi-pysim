import asyncio
import time

from EnvironmentDavid.babylon import BABYLON_LiveBackend
from scioi_py_core.core.objects import VisulizationEnvironment, ObstacleBox, BabylonRobot, AreaBox, Door, Switch, Goal
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotPhysicalObject, TankRobotSimObject
import threading


class BayblonVisualization(VisulizationEnvironment):
    """
    this class has all the elements relevant for the babylon visualization of the Testbed
    """
    size_x = 5.094  # size x of testbed in m
    size_y = 3.679  # size y of testbed in m
    tiles_x = 18
    tiles_y = 13
    base_height = 0.150
    wall_thickness = 0.010
    webapp = None

    def __init__(self):
        super().__init__()

    def add_simulated_agent(self, *args: TankRobotPhysicalObject or TankRobotSimObject):
        """
        add another agent to the environment
        """
        for element in args:
            # self.robots.append(BabylonRobot(element.length, element.width, element.height))
            self.robot_list.append(element)

    def start_babylon(self):
        # write all objects into jason
        self.toJson(file="../babylon/objects.json")
        babylon_thread = threading.Thread(target=self._start_webapp)
        babylon_thread.start()
        time.sleep(1)  # todo

    def goal_reached_cb(self, *args, **kwargs):
        pass

    def _start_webapp(self):

        asyncio.set_event_loop(asyncio.new_event_loop())
        self.webapp = BABYLON_LiveBackend("../babylon/example_LNDW_simple.html", options={})
        self.webapp.start()
        while True:
            time.sleep(0.1)
