import enum
import json
import math
import time

import numpy as np
from matplotlib import pyplot as plt

from EnvironmentDavid.baseline.robot_simulation import RobotSimulation
from EnvironmentDavid.Objects.EnvironmentDavid_Agents import TankRobotSimObject, TankRobotPhysicalObject
from scioi_py_core.utils.joystick.joystick_manager import Joystick
from scioi_py_core.utils.orientations import psiFromRotMat


class Box:
    center: np.ndarray
    size_x: float
    size_y: float
    height: float
    psi: float

    visible: bool
    name: str

    def __init__(self, center, size_x, size_y, psi, height: float = 100, edge_discretization=10, visible: bool = True):
        self.center = np.asarray(center)
        self.size_x = size_x
        self.size_y = size_y
        self.height = height
        self.psi = psi
        self.edge_discretization = edge_discretization
        self.visible = visible

    @property
    def R(self):
        return np.asarray([[np.cos(self.psi), -np.sin(self.psi)], [np.sin(self.psi), np.cos(self.psi)]])

    def getVertices(self):
        point_1 = self.R @ np.asarray([self.size_x / 2, self.size_y / 2]) + self.center
        point_2 = self.R @ np.asarray([-self.size_x / 2, self.size_y / 2]) + self.center
        point_3 = self.R @ np.asarray([-self.size_x / 2, -self.size_y / 2]) + self.center
        point_4 = self.R @ np.asarray([self.size_x / 2, -self.size_y / 2]) + self.center

        return [point_1, point_2, point_3, point_4]

    def getEdgePoints(self):

        # front-left
        points_front_left = []
        for i in range(0, self.edge_discretization + 1):
            p = np.array([self.size_x / 2, (self.size_y / 2) * (i / self.edge_discretization)])
            points_front_left.append(self.R @ p + self.center)

        # left-front
        points_left_front = []
        for i in range(0, self.edge_discretization + 1):
            p = np.array([(self.size_x / 2) * (i / self.edge_discretization), self.size_y / 2])
            points_left_front.append(self.R @ p + self.center)

        # left-back
        points_left_back = []
        for i in range(0, self.edge_discretization + 1):
            p = np.array([-(self.size_x / 2) * (i / self.edge_discretization), self.size_y / 2])
            points_left_back.append(self.R @ p + self.center)

        # back-left
        points_back_left = []
        for i in range(0, self.edge_discretization + 1):
            p = np.array([-(self.size_x / 2), (self.size_y / 2) * (i / self.edge_discretization)])
            points_back_left.append(self.R @ p + self.center)

        # back-right
        points_back_right = []
        for i in range(0, self.edge_discretization + 1):
            p = np.array([-(self.size_x / 2), -(self.size_y / 2) * (i / self.edge_discretization)])
            points_back_right.append(self.R @ p + self.center)

        # right_back
        points_right_back = []
        for i in range(0, self.edge_discretization + 1):
            p = np.array([-(self.size_x / 2) * (i / self.edge_discretization), -(self.size_y / 2)])
            points_right_back.append(self.R @ p + self.center)

        # right-front
        points_right_front = []
        for i in range(0, self.edge_discretization + 1):
            p = np.array([(self.size_x / 2) * (i / self.edge_discretization), -(self.size_y / 2)])
            points_right_front.append(self.R @ p + self.center)

        # front-right
        points_front_right = []
        for i in range(0, self.edge_discretization + 1):
            p = np.array([(self.size_x / 2), -(self.size_y / 2) * (i / self.edge_discretization)])
            points_front_right.append(self.R @ p + self.center)

        output = {
            'front_left': points_front_left,
            'left_front': points_left_front,
            'left_back': points_left_back,
            'back_left': points_back_left,
            'back_right': points_back_right,
            'right_back': points_right_back,
            'right_front': points_right_front,
            'front_right': points_front_right,
        }
        return output

    def collision(self, other: 'Box'):
        """
        :param other:
        :return:
        """
        collided_vertices = []
        collided_areas = []

        R_T_other = other.R.T
        for area, points in self.getEdgePoints().items():
            for point in points:
                vec_rel = point - other.center
                vec_rel_trans = R_T_other @ vec_rel
                if abs(vec_rel_trans[0]) <= other.size_x / 2 and abs(vec_rel_trans[1]) <= other.size_y / 2:
                    collided_vertices.append(point)
                    if area not in collided_areas:
                        collided_areas.append(area)
        return collided_areas, collided_vertices


class BoxPlot:
    rectangles: list[Box]

    def __init__(self, rectangles: list[Box], collision=False):
        ax = plt.subplot()
        color = 'k'
        for rect in rectangles:
            p = rect.getVertices()
            p1 = p[0]
            p2 = p[1]
            p3 = p[2]
            p4 = p[3]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color)
            ax.plot([p2[0], p3[0]], [p2[1], p3[1]], color)
            ax.plot([p3[0], p4[0]], [p3[1], p4[1]], color)
            ax.plot([p4[0], p1[0]], [p4[1], p1[1]], color)

            if collision:
                edge_points = rect.getEdgePoints()
                for key, value in edge_points.items():
                    for point in value:
                        ax.plot(point[0], point[1], 'ko')

                for other in [rec for rec in rectangles if rec is not rect]:
                    _, collided_vertices = rect.collision(other)
                    for cv in collided_vertices:
                        ax.plot(cv[0], cv[1], 'ro')

        ax.set_aspect('equal')
        plt.grid()
        plt.show()


class TileBoxOrientation(enum.Enum):
    H = 0,
    V = 1


class ObstacleBox(Box):
    type = 'Obstacle'

    @classmethod
    def fromTiles(cls, orientation: TileBoxOrientation, start_tile_x: int, start_tile_y: int, number_tiles: int,
                  tile_size: float, wall_thickness: float, edge_discretization, **kwargs):

        if isinstance(orientation, str):
            if orientation == 'v':
                orientation = TileBoxOrientation.V
            elif orientation == 'h':
                orientation = TileBoxOrientation.H
            else:
                raise Exception

        boxes = []
        for i in range(0, number_tiles):
            if orientation == TileBoxOrientation.H:
                center = [(start_tile_x * tile_size + tile_size / 2) + tile_size * i, start_tile_y * tile_size]
                box = cls(center=center, size_x=tile_size, size_y=wall_thickness, psi=0,
                          edge_discretization=edge_discretization, **kwargs)
                box.orientation = orientation
            elif orientation == TileBoxOrientation.V:
                center = [start_tile_x * tile_size, (start_tile_y * tile_size + tile_size / 2) + tile_size * i]
                box = cls(center=center, size_x=tile_size, size_y=wall_thickness, psi=math.pi / 2,
                          edge_discretization=edge_discretization, **kwargs)
                box.orientation = orientation
            boxes.append(box)
        return boxes


class AreaBox(Box):
    type = 'Area'
    pass


class RobotBox(Box):
    pass


class BabylonRobot:
    # todo: get rid of this class
    collisionBox: RobotBox
    position: list
    psi: float

    length: float
    width: float
    height: float

    collision: bool
    collisionAreas: list

    id: int

    joystick: Joystick

    env: 'VisulizationEnvironment'

    simulation: RobotSimulation

    _last_collision_state: bool

    # counter used to set an id for each robot for babylon
    robot_counter = 0

    def __init__(self, length, width, height):
        self.length = length
        self.width = width
        self.height = height
        self.id = self.robot_counter
        self.robot_counter += 1

        # self.env = environment

        self.collisionAreas = []

        self.simulation = None

        position = [0, 0]
        psi = [0, 0]

        self.collisionBox = RobotBox(center=position, size_x=length, size_y=width, psi=psi,
                                     height=self.height,
                                     edge_discretization=10)
        self.position = position
        self.psi = psi
        self.collision = False
        self.joystick = None
        self._last_collision_state = False

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self.collisionBox.center = value
        if self.simulation is not None:
            self.simulation.position = value

    @property
    def psi(self):
        return self._psi

    @psi.setter
    def psi(self, value):
        self._psi = value
        self.collisionBox.psi = value
        if self.simulation is not None:
            self.simulation.psi = value

    @property
    def cell(self):
        return self.env.getCellByPosition(self.position[0], self.position[1])

    def calcInput(self, v, psi_dot):
        if 'front_left' in self.collisionAreas or 'front_right' in self.collisionAreas or 'left_front' in self.collisionAreas or 'right_front' in self.collisionAreas:
            if v > 0:
                v = 0

        if 'back_left' in self.collisionAreas or 'back_right' in self.collisionAreas or 'left_back' in self.collisionAreas or 'right_back' in self.collisionAreas:
            if v < 0:
                v = 0

        if 'left_front' in self.collisionAreas:
            if psi_dot > 0:
                psi_dot = 0

        if 'front_left' in self.collisionAreas and 'left_front' not in self.collisionAreas:
            if psi_dot < 0:
                psi_dot = 0

        if 'right_front' in self.collisionAreas:
            if psi_dot < 0:
                psi_dot = 0

        if 'front_right' in self.collisionAreas and 'right_front' not in self.collisionAreas:
            if psi_dot > 0:
                psi_dot = 0

        if 'left_back' in self.collisionAreas:
            if psi_dot < 0:
                psi_dot = 0

        if 'back_left' in self.collisionAreas and 'left_back' not in self.collisionAreas:
            if psi_dot > 0:
                psi_dot = 0

        if 'right_back' in self.collisionAreas:
            if psi_dot > 0:
                psi_dot = 0

        if 'back_right' in self.collisionAreas and 'right_back' not in self.collisionAreas:
            if psi_dot < 0:
                psi_dot = 0

        return v, psi_dot

    # ------------------------------------------------------------------------------------------------------------------
    def collisionDetection(self):
        """
        - check for collision of the robots
        - create cluster from current robot position
        - check collision of robots with every wall, door or area that belongs to the cells which are in the cluster
        :return:
        """
        self.collision = False
        # Get the collidable_objects that are interesting for us
        robot_cell = self.env.getCellByPosition(self.position[0], self.position[1])
        if robot_cell is None:
            return
        cell_cluster = self.env.getCellCluster(robot_cell.x, robot_cell.y)

        collidable_objects = []  # todo: easier to give the cells all the collidable_objects as property -> cell class?
        for cell in cell_cluster:
            for wall in cell.walls:
                if wall not in collidable_objects:
                    collidable_objects.append(wall)

        for name, door in self.env.doors.items():  # todo: work with a property like collidable?
            if not door.open_state:
                collidable_objects.append(door)

        self.collisionAreas = []
        for wall in collidable_objects:
            ca, cv = self.collisionBox.collision(wall)
            for area in ca:
                if area not in self.collisionAreas:
                    self.collisionAreas.append(area)

        if len(self.collisionAreas) > 0:
            self.collision = True

        if self.collision and not self._last_collision_state and self.joystick is not None:
            self.joystick.rumble(1, 0.3)

        self._last_collision_state = self.collision

        return self.collisionAreas

    def addSimulation(self, Ts):
        self.simulation = RobotSimulation(Ts=Ts)

    def updateSimulation(self, input):
        self.simulation.update(input)
        self.position = self.simulation.position
        self.psi = self.simulation.psi


class FloorTile(Box):
    floor_state: int
    height = 1

    def __init__(self, center, size_x, size_y, psi, height=100, edge_discretization=10, visible: bool = True):
        super().__init__(center, size_x, size_y, psi, height=self.height, edge_discretization=10, visible=True)
        self.floor_state = 0


class Wall(ObstacleBox):
    wall_state: int
    orientation: str

    def __init__(self, center, size_x, size_y, psi, height=100, edge_discretization=10, visible: bool = True):
        super().__init__(center, size_x, size_y, psi, height=100, edge_discretization=1, visible=True)
        self.wall_state = 0
        if self.psi == 0:
            self.orientation = 'h'
        else:
            self.orientation = 'v'


class Door(ObstacleBox):
    open_state: int
    circuit_id: int
    switches: list

    def __init__(self, id, switches, center, size_x, size_y, psi, **kwargs):
        super().__init__(center, size_x, size_y, psi)

        self.open_state = False
        self.circuit_id = id
        self.switches = switches
        self.visible = False

    def check(self):
        if all(sw.switch_state for sw in self.switches):
            self.open_state = True
        else:
            self.open_state = False


class Switch:
    switch_state: int
    momentary: bool
    cell: list
    circuit_id: int
    door: Door

    def __init__(self, cell: list, momentary, id):
        self.cell = cell
        self.momentary = momentary
        self.switch_state = False
        self.circuit_id = id
        self.door = None

    def check(self, robots: dict[str, BabylonRobot]):

        if any(self.cell == [robot.cell.x, robot.cell.y] for robot in robots.values()):
            if self.door.visible:
                self.switch_state = True
        else:
            if self.momentary:
                if self.door.visible:
                    self.switch_state = False


class Goal:
    cell: list
    condition: str  # 'any' or 'all'
    callback: callable
    reached: bool

    discovered: bool
    visible: bool

    def __init__(self, cell, condition, callback, visible):
        self.cell = cell
        self.condition = condition
        self.callback = callback
        self.reached = False
        self.visible = visible
        self.discovered = False

    def check(self, robots: list):
        reached_robots = []

        for robot in robots:
            if self.cell == [robot.cell.x, robot.cell.y]:
                reached_robots.append(robot)

        if self.condition == 'any' and len(reached_robots) > 0:
            self.reached = True
            self.callback(reached_robots)
        elif self.condition == 'all' and len(reached_robots) == len(robots):
            self.reached = True
            self.callback(reached_robots)


class Cell:
    x: int
    y: int
    visited: bool
    floor_tile: FloorTile
    walls: list[Wall]
    doors: list[Door]
    goal: Goal

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visited = False
        self.walls = []
        self.doors = []
        self.goal = None


class VisulizationEnvironment:
    groundBox: Box
    obstacles: list[ObstacleBox]

    walls: list[Wall]
    floortiles: dict[str, Box]
    # robots: dict[str, BabylonRobot]
    robot_list: list[TankRobotPhysicalObject or TankRobotSimObject]
    areas: dict[str, AreaBox]
    switches: dict[str, Switch]
    doors: dict[str, Door]
    goals: dict[str, Goal]

    cells: list[Cell]

    size_x: float
    size_y: float
    tiles_x: int
    tiles_y: int

    base_height: float
    wall_thickness: float

    def __init__(self):
        self.obstacles = []
        self.cells = []
        self.walls = []
        # self.robots: BabylonRobot = []
        self.robot_list = []
        self.switches = {}
        self.doors = {}
        self.goals = {}

        for x in range(0, self.tiles_x):
            for y in range(0, self.tiles_y):
                self.cells.append(Cell(x=x, y=y))

        self.generateBorders()
        self.floortiles = self.generateFloor()

        self.start_time = time.time()

    def wallsFromList(self, wall_list):
        for entry in wall_list:
            orientation = entry[0]
            start_tile_x = entry[1]
            start_tile_y = entry[2]
            num_tiles = entry[3]
            walls = Wall.fromTiles(orientation, start_tile_x, start_tile_y, num_tiles,
                                   tile_size=self.size_x / self.tiles_x, wall_thickness=self.wall_thickness,
                                   edge_discretization=1)

            for wall in walls:
                wall.visible = False
                self.walls.append(wall)

        for wall in self.walls:
            x = wall.center[0]
            y = wall.center[1]

            if wall.orientation == 'h' or wall.orientation == TileBoxOrientation.H:
                cell1 = self.getCellByPosition(x, y + self.tile_size / 2)
                cell2 = self.getCellByPosition(x, y - self.tile_size / 2)
            else:
                cell1 = self.getCellByPosition(x + self.tile_size / 2, y)
                cell2 = self.getCellByPosition(x - self.tile_size / 2, y)

            if cell1 is not None and wall not in cell1.walls:
                cell1.walls.append(wall)
            if cell2 is not None and wall not in cell2.walls:
                cell2.walls.append(wall)

    def toJson(self, file=None):
        json_dict = {
            'obstacles': {},
            'robots': {},
            'areas': {},
            'floor': {},
            'walls': {},
            'switches': {},
            'doors': {},
            'goals': {}
        }
        for idx, wall in enumerate(self.walls):
            wall_name = f"Wall_{idx}"
            wall.name = wall_name
            wall_dict = {
                'center_x': wall.center[0],
                'center_y': wall.center[1],
                'psi': wall.psi,
                'width': wall.size_x,
                'length': wall.size_y,
                'height': wall.height,
                'state': wall.wall_state,
                # 'visible': wall.visible,
                'visible': True,  # todo: remove
                'type': 'Wall'
            }
            json_dict['walls'][wall_name] = wall_dict

        for idx, obstacle in enumerate(self.obstacles):
            obstacle_name = f"Obstacle_{idx}"
            obstacle.name = obstacle_name
            obstacle_dict = {
                'center_x': obstacle.center[0],
                'center_y': obstacle.center[1],
                'psi': obstacle.psi,
                'width': obstacle.size_x,
                'length': obstacle.size_y,
                'height': obstacle.height,
                'type': 'Obstacle'
            }
            json_dict['obstacles'][obstacle_name] = obstacle_dict

        for name, tile in self.floortiles.items():
            tile_dict = {
                'center_x': tile.center[0],
                'center_y': tile.center[1],
                'psi': tile.psi,
                'width': tile.size_x,
                'length': tile.size_y,
                'height': tile.height,
                'type': 'Floor'
            }
            json_dict['floor'][name] = tile_dict

        for idx, robot in enumerate(self.robot_list):
            orientation_test = robot.physics.bounding_objects['body'].orientation
            robot_name = f"{idx}"
            robot_dict = {
                'id': 0,
                'position': list(robot.physics.bounding_objects['body'].position),
                'length': robot.physics.length,
                'width': robot.physics.width,
                'height': robot.physics.height,
                'psi': psiFromRotMat(robot.configuration['rot']),
                'name': f'robot{robot_name}'
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

    @property
    def tile_size(self):
        return self.size_x / self.tiles_x

    def generateBorders(self):
        wall1 = Wall.fromTiles('h', 0, 0, self.tiles_x, tile_size=self.size_x / self.tiles_x,
                               wall_thickness=self.wall_thickness, edge_discretization=1)

        wall2 = Wall.fromTiles('v', 0, 0, self.tiles_y, tile_size=self.size_x / self.tiles_x,
                               wall_thickness=self.wall_thickness, edge_discretization=1)

        wall3 = Wall.fromTiles('h', 0, self.tiles_y, self.tiles_x, tile_size=self.size_x / self.tiles_x,
                               wall_thickness=self.wall_thickness, edge_discretization=1)

        wall4 = Wall.fromTiles('v', self.tiles_x, 0, self.tiles_y, tile_size=self.size_x / self.tiles_x,
                               wall_thickness=self.wall_thickness, edge_discretization=1)

        for wall in wall1:
            self.walls.append(wall)
        for wall in wall2:
            self.walls.append(wall)
        for wall in wall3:
            self.walls.append(wall)
        for wall in wall4:
            self.walls.append(wall)

        for wall in self.walls:
            x = wall.center[0]
            y = wall.center[1]

            if wall.orientation == 'h' or wall.orientation == TileBoxOrientation.H:
                cell1 = self.getCellByPosition(x, y + self.tile_size / 2)
                cell2 = self.getCellByPosition(x, y - self.tile_size / 2)
            else:
                cell1 = self.getCellByPosition(x + self.tile_size / 2, y)
                cell2 = self.getCellByPosition(x - self.tile_size / 2, y)

            if cell1 is None and cell2 is None:
                pass
            if cell1 is not None and wall not in cell1.walls:
                cell1.walls.append(wall)
            if cell2 is not None and wall not in cell2.walls:
                cell2.walls.append(wall)

    def getCell(self, x, y):

        return next((cell for cell in self.cells if cell.x == x and cell.y == y), None)

    # ------------------------------------------------------------------------------------------------------------------
    def getCellByPosition(self, x_pos, y_pos):
        # print(f'x_pos {x_pos}')
        # print(f'y_pos{y_pos}')
        x = int(math.floor(x_pos / self.tile_size))
        y = int(math.floor(y_pos / self.tile_size))

        return self.getCell(x, y)

    # ------------------------------------------------------------------------------------------------------------------
    def getCellPosition(self, cell):
        if isinstance(cell, Cell):
            return [cell.x * self.tile_size + self.tile_size / 2, cell.y * self.tile_size + self.tile_size / 2]
        elif isinstance(cell, list):
            cell = self.getCell(cell[0], cell[1])
            return [cell.x * self.tile_size + self.tile_size / 2, cell.y * self.tile_size + self.tile_size / 2]

    # ------------------------------------------------------------------------------------------------------------------
    def generateFloor(self):
        floor_tiles = {}
        for x in range(0, self.tiles_x):
            for y in range(0, self.tiles_y):
                tile = FloorTile(
                    center=[self.tile_size / 2 + x * self.tile_size, self.tile_size / 2 + y * self.tile_size],
                    size_x=self.tile_size, size_y=self.tile_size, psi=0, height=1, edge_discretization=1)
                name = f"Floor_{x}_{y}"
                tile.name = name
                floor_tiles[name] = tile

                cell = self.getCell(x, y)
                cell.floor_tile = tile

        return floor_tiles

    def generateSample(self):
        sample = {'robots': {},
                  'floor': {},
                  'walls': {},
                  'doors': {},
                  'switches': {},
                  'goals': {}}

        # for count, robot in enumerate(self.robots):
        for count, robot in enumerate(self.robot_list):
            robot_sample = {
                'position': robot.physics.bounding_objects['body'].position,
                'psi': psiFromRotMat(robot.physics.bounding_objects['body'].orientation),
                # 'collision': robot.collision
                'collision': 0
            }
            sample['robots'][f'{count}'] = robot_sample
            # sample['robots'] = robot_sample

        discovered_walls = []

        sample['t'] = time.time() - self.start_time

        return sample

    # ------------------------------------------------------------------------------------------------------------------
    def getCellCluster(self, x, y):
        """
        get a cluster of cells from the current position for collision detection
        :param x: current position x
        :param y: current position y
        :return: cell cluster
        """
        cells = []

        for _x in range(x - 1, x + 2):
            cell = self.getCell(_x, y)
            if cell is not None and cell not in cells:
                cells.append(cell)

            for _y in range(y - 1, y + 2):
                cell = self.getCell(x, _y)
                if cell is not None and cell not in cells:
                    cells.append(cell)
        return cells

    # ------------------------------------------------------------------------------------------------------------------
    def collisionDetection(self):
        for name, robot in self.robots.items():
            robot.collisionDetection()

    # ------------------------------------------------------------------------------------------------------------------
    def build(self):
        for name, door in self.doors.items():
            if door.orientation == 'h':
                cell1 = self.getCellByPosition(door.center[0], door.center[1] + self.tile_size / 2)
                cell2 = self.getCellByPosition(door.center[0], door.center[1] - self.tile_size / 2)
            else:
                cell1 = self.getCellByPosition(door.center[0] + self.tile_size / 2, door.center[1])
                cell2 = self.getCellByPosition(door.center[0] - self.tile_size / 2, door.center[1])

            if cell1 is not None and door not in cell1.doors:
                cell1.doors.append(door)
            if cell2 is not None and door not in cell2.doors:
                cell2.doors.append(door)

        for name, goal in self.goals.items():
            cell = self.getCell(goal.cell[0], goal.cell[1])
            cell.goal = goal

        for name, door in self.doors.items():
            for sw in door.switches:
                sw.door = door
