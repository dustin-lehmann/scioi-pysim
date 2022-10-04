import asyncio
import time

from EnvironmentDavid.babylon import BABYLON_LiveBackend
from EnvironmentDavid.babylon_core.babylon_objects import BabylonVisualizationEnvironment
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject
from scioi_py_core.core.obstacles import Obstacle
import threading


class BabylonVisualization(BabylonVisualizationEnvironment):
    """
    this class has all the elements relevant for the babylon visualization of the Testbed
    """
    webapp = None

    def __init__(self):
        super().__init__()

    def add_object_to_babylon(self, *args: 'TankRobotSimObject |Obstacle') -> None:         #todo: multiple type hints really look like that?
        """
        - add one or multiple objects to the babylon Visualization
        - depending on if it is a standard obstacle or a robots it gets added to one of the respective lists
        """
        for element in args:
            if isinstance(element, TankRobotSimObject):
                self.robots_list.append(element)

            elif isinstance(element, Obstacle):
                self.obstacles_list.append(element)


            else:
                raise Exception('there is no matching list for this object type!')

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
