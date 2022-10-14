import json
import time

from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject
from scioi_py_core.utils.orientations import psiFromRotMat
from scioi_py_core.core.obstacles import Obstacle
from scioi_py_core.core.world import WorldObject


class BabylonVisualizationEnvironment:
    # # list where all not moving objects are stored
    # obstacles_list: list['Obstacle']
    # # list with all the robot_textures that are active in the testbed
    # robots_list: list['TankRobotSimObject']
    babylon_objects_dict: dict

    size_x: float
    size_y: float
    tiles_x: int
    tiles_y: int

    base_height: float
    wall_thickness: float

    def __init__(self, texture_settings=None, *args, **kwargs):
        self.texture_settings = texture_settings

        # self.obstacles_list = []
        # self.robots_list = []
        self.babylon_objects_dict = {}

        self.start_time = time.time()

    def toJson(self, file=None):
        json_dict = {'textures': self.texture_settings, 'objects': {}}
        # textures

        json_dict['objects'] = self.babylon_objects_dict['world'] #todo: uncomment
        # # obstacles
        # for idx, obstacle in enumerate(self.obstacles_list):
        #     obstacle_name = f"Obstacle_{idx}"
        #
        #     obstacle_dict = {
        #         'center_x': obstacle.configuration['x'],  # todo: give an array
        #         'center_y': obstacle.configuration['y'],
        #         'center_z': obstacle.configuration['z'],
        #         'psi': psiFromRotMat(obstacle.configuration['rot']),
        #         'length': obstacle.physics.bounding_objects['cuboid'].dimensions[0],
        #         'width': obstacle.physics.bounding_objects['cuboid'].dimensions[1],
        #         'height': obstacle.physics.bounding_objects['cuboid'].dimensions[2],
        #         'visible': obstacle.visible,
        #         'name': obstacle.name,
        #         'type': obstacle.type,
        #         'id': obstacle.id
        #     }
        #     json_dict['environment'][obstacle_name] = obstacle_dict
        #
        # # robots
        # for idx, robot in enumerate(self.robots_list):
        #     orientation_test = robot.physics.bounding_objects['body'].orientation
        #
        #     robot_dict = {
        #         'position': list(robot.physics.bounding_objects['body'].position),
        #         'length': robot.physics.length,
        #         'width': robot.physics.width,
        #         'height': robot.physics.height,
        #         'psi': psiFromRotMat(robot.configuration['rot']),
        #         'name': robot.name,
        #         'type': robot.type,
        #         'id': robot.id
        #     }
        #     json_dict['robots'][robot.name] = robot_dict

        if file is not None:
            try:
                with open(file, 'x') as outfile:
                    json.dump(json_dict, outfile, indent=2)
            except FileExistsError:
                with open(file, 'w') as outfile:
                    json.dump(json_dict, outfile, indent=2)

        return json.dumps(json_dict, indent=2)

    def dict_to_json(self, objects_list: list, json_dict):
        for idx, obstacle in enumerate(objects_list):
            obstacle_name = f"Obstacle_{idx}"
            obstacle.name = obstacle_name  # todo: removable?
            obstacle_dict = {
                'center_x': obstacle.configuration['x'],
                'center_y': obstacle.configuration['y'],
                'center_z': obstacle.configuration['z'],
                'psi': psiFromRotMat(obstacle['rot']),
                'length': obstacle.physics.dimensions[0],
                'width': obstacle.physics.dimensions[1],
                'height': obstacle.physics.dimensions[0],
                'type': obstacle.type
            }
            json_dict['environment'][obstacle_name] = obstacle_dict

    def generate_sample(self):
        """
        generate a sample with data for:
        -robots (position
        -objects
        -elapsed time
        :return:
        """
        sample = self.babylon_objects_dict

        sample['t'] = time.time() - self.start_time

        # remove deleted items from dict with currently existing items
        self.babylon_objects_dict['existing'] = {k: self.babylon_objects_dict['existing'][k] for k in
                                                 self.babylon_objects_dict['existing'] if
                                                 k not in self.babylon_objects_dict['deleted']}
        # add all newly added items to existing items
        self.babylon_objects_dict['existing'] = self.babylon_objects_dict['existing'] | \
                                                self.babylon_objects_dict['added']

        return sample

    # ------------------------------------------------------------------------------------------------------------------
    # def getCellCluster(self, x, y):
    #     """
    #     get a cluster of cells from the current position for collision detection
    #     :param x: current position x
    #     :param y: current position y
    #     :return: cell cluster
    #     """
    #     cells = []
    #
    #     for _x in range(x - 1, x + 2):
    #         cell = self.getCell(_x, y)
    #         if cell is not None and cell not in cells:
    #             cells.append(cell)
    #
    #         for _y in range(y - 1, y + 2):
    #             cell = self.getCell(x, _y)
    #             if cell is not None and cell not in cells:
    #                 cells.append(cell)
    #     return cells

    # ------------------------------------------------------------------------------------------------------------------
    # def collisionDetection(self):
    #     for name, robot in self.robot_textures.items():
    #         robot.collisionDetection()

    # ------------------------------------------------------------------------------------------------------------------
    # def build(self):
    #     for name, door in self.doors.items():
    #         if door.orientation == 'h':
    #             cell1 = self.getCellByPosition(door.center[0], door.center[1] + self.tile_size / 2)
    #             cell2 = self.getCellByPosition(door.center[0], door.center[1] - self.tile_size / 2)
    #         else:
    #             cell1 = self.getCellByPosition(door.center[0] + self.tile_size / 2, door.center[1])
    #             cell2 = self.getCellByPosition(door.center[0] - self.tile_size / 2, door.center[1])
    #
    #         if cell1 is not None and door not in cell1.doors:
    #             cell1.doors.append(door)
    #         if cell2 is not None and door not in cell2.doors:
    #             cell2.doors.append(door)
    #
    #     for name, goal in self.goals.items():
    #         cell = self.getCell(goal.cell[0], goal.cell[1])
    #         cell.goal = goal
    #
    #     for name, door in self.doors.items():
    #         for sw in door.switches:
    #             sw.door = door
