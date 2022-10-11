import json
import time

from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject
from scioi_py_core.utils.orientations import psiFromRotMat
from scioi_py_core.core.obstacles import Obstacle


class BabylonVisualizationEnvironment:

    # list where all not moving objects are stored
    obstacles_list: ['Obstacle']
    # list with all the robot_textures that are active in the testbed
    robots_list: list['TankRobotSimObject']

    size_x: float
    size_y: float
    tiles_x: int
    tiles_y: int

    base_height: float
    wall_thickness: float

    def __init__(self, texture_settings=None, *args, **kwargs):
        self.texture_settings = texture_settings
        self.obstacles_list = []
        self.robots_list = []

        self.start_time = time.time()

    def toJson(self, file=None):
        json_dict = {'textures': self.texture_settings, 'environment': {}, 'robots': {}}
        # textures

        # obstacles
        for idx, obstacle in enumerate(self.obstacles_list):
            obstacle_name = f"Obstacle_{idx}"

            obstacle_dict = {
                'center_x': obstacle.configuration['x'],
                'center_y': obstacle.configuration['y'],
                'center_z': obstacle.configuration['z'],
                'psi': psiFromRotMat(obstacle.configuration['rot']),
                'length': obstacle.physics.bounding_objects['cuboid'].dimensions[0],
                'width': obstacle.physics.bounding_objects['cuboid'].dimensions[1],
                'height': obstacle.physics.bounding_objects['cuboid'].dimensions[2],
                'type': obstacle.type,
                'visible': obstacle.visible,
                'name': obstacle.name
            }
            json_dict['environment'][obstacle_name] = obstacle_dict

        # robots
        for idx, robot in enumerate(self.robots_list):
            orientation_test = robot.physics.bounding_objects['body'].orientation
            robot_name = f"{idx}"
            robot_dict = {
                'id': 0,
                'position': list(robot.physics.bounding_objects['body'].position),
                'length': robot.physics.length,
                'width': robot.physics.width,
                'height': robot.physics.height,
                'psi': psiFromRotMat(robot.configuration['rot']),
                'name': f'robot{robot_name}',
                'type': robot.type
            }
            json_dict['robots'][robot_name] = robot_dict

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

    # @property
    # def tile_size(self):
    #     return self.size_x / self.tiles_x

    # def generateBorders(self):
    #     wall1 = Wall.fromTiles('h', 0, 0, self.tiles_x, tile_size=self.size_x / self.tiles_x,
    #                            wall_thickness=self.wall_thickness, edge_discretization=1)
    #
    #     wall2 = Wall.fromTiles('v', 0, 0, self.tiles_y, tile_size=self.size_x / self.tiles_x,
    #                            wall_thickness=self.wall_thickness, edge_discretization=1)
    #
    #     wall3 = Wall.fromTiles('h', 0, self.tiles_y, self.tiles_x, tile_size=self.size_x / self.tiles_x,
    #                            wall_thickness=self.wall_thickness, edge_discretization=1)
    #
    #     wall4 = Wall.fromTiles('v', self.tiles_x, 0, self.tiles_y, tile_size=self.size_x / self.tiles_x,
    #                            wall_thickness=self.wall_thickness, edge_discretization=1)
    #
    #     for wall in wall1:
    #         self.walls.append(wall)
    #     for wall in wall2:
    #         self.walls.append(wall)
    #     for wall in wall3:
    #         self.walls.append(wall)
    #     for wall in wall4:
    #         self.walls.append(wall)
    #
    #     for wall in self.walls:
    #         x = wall.center[0]
    #         y = wall.center[1]
    #
    #         if wall.orientation == 'h' or wall.orientation == TileBoxOrientation.H:
    #             cell1 = self.getCellByPosition(x, y + self.tile_size / 2)
    #             cell2 = self.getCellByPosition(x, y - self.tile_size / 2)
    #         else:
    #             cell1 = self.getCellByPosition(x + self.tile_size / 2, y)
    #             cell2 = self.getCellByPosition(x - self.tile_size / 2, y)
    #
    #         if cell1 is None and cell2 is None:
    #             pass
    #         if cell1 is not None and wall not in cell1.walls:
    #             cell1.walls.append(wall)
    #         if cell2 is not None and wall not in cell2.walls:
    #             cell2.walls.append(wall)

    # def getCell(self, x, y):
    #
    #     return next((cell for cell in self.cells if cell.x == x and cell.y == y), None)

    # ------------------------------------------------------------------------------------------------------------------
    # def getCellByPosition(self, x_pos, y_pos):
    #     # print(f'x_pos {x_pos}')
    #     # print(f'y_pos{y_pos}')
    #     x = int(math.floor(x_pos / self.tile_size))
    #     y = int(math.floor(y_pos / self.tile_size))
    #
    #     return self.getCell(x, y)

    # ------------------------------------------------------------------------------------------------------------------
    # def getCellPosition(self, cell):
    #     if isinstance(cell, Cell):
    #         return [cell.x * self.tile_size + self.tile_size / 2, cell.y * self.tile_size + self.tile_size / 2]
    #     elif isinstance(cell, list):
    #         cell = self.getCell(cell[0], cell[1])
    #         return [cell.x * self.tile_size + self.tile_size / 2, cell.y * self.tile_size + self.tile_size / 2]

    # ------------------------------------------------------------------------------------------------------------------
    # def generateFloor(self):
    #     floor_tiles = {}
    #     for x in range(0, self.tiles_x):
    #         for y in range(0, self.tiles_y):
    #             tile = FloorTile(
    #                 center=[self.tile_size / 2 + x * self.tile_size, self.tile_size / 2 + y * self.tile_size],
    #                 size_x=self.tile_size, size_y=self.tile_size, psi=0, height=1, edge_discretization=1)
    #             name = f"Floor_{x}_{y}"
    #             tile.name = name
    #             floor_tiles[name] = tile
    #
    #             cell = self.getCell(x, y)
    #             cell.floor_tile = tile
    #
    #     return floor_tiles

    def generateSample(self):
        sample = {'robots': {},
                  'floor': {},
                  'walls': {},
                  'doors': {},
                  'switches': {},
                  'goals': {}}

        # for count, robot in enumerate(self.robot_textures):
        for count, robot in enumerate(self.robots_list):
            robot_sample = {
                'position': robot.physics.bounding_objects['body'].position,
                'psi': psiFromRotMat(robot.physics.bounding_objects['body'].orientation),
                # 'collision': robot.collision
                'collision': 0
            }
            sample['robots'][f'{count}'] = robot_sample
            # sample['robot_textures'] = robot_sample

        discovered_walls = []

        sample['t'] = time.time() - self.start_time

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
