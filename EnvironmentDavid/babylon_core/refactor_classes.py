import numpy as np

# from objects import Box


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


class Object:
    """
    Base Class for every object of Testbed
    """
    position: list[2]
    orientation: float
    visible: bool


class PhysicalObject(Object):
    """
    - Object can be physically interacted with
    - can be real or simulated
    """
    collidable: bool
    Box: Box


class Sensor:
    pass


class VirtualSensor(Sensor):
    """
    Sensor is only simulated
    """
    pass


class RealSensor(Sensor):
    """
    real Sensor object in testbed
    """
    pass


class Agent(PhysicalObject):
    pass


class VirtualAgent(Agent):
    """
    Agent is only simulated
    """
    pass


class RealAgent(Agent):
    """
    Real Agent e.g. Robot in testbed
    """
    pass


class Obstacle(PhysicalObject):
    """
    the Physical object is an obstacle that can collide with other obstacles
    """
    pass


class Wall(Obstacle):
    """
    wall that keeps robot_textures from driving through
    """
    pass


class TileWall(Wall):
    """
    wall that is placed on the edge of a tile
    """
    pass


class Floor(Obstacle):
    """
    floor of the Testbed
    """
    pass


class TiledFloor(Floor):
    """
    floor that is devided in tiles
    """
    pass


class GameCircuitObject:
    """
    connects Environment with each other so they can interact
    """
    activation_state: bool

    def __init__(self, activation_state):
        self.activation_state = activation_state



class Button(Obstacle, GameCircuitObject):
    """
    buttons can open the doors they are connected to via the GameCircuit
    """
    def __init__(self):
        pass



class Doorcircuit(GameCircuitObject):
    """
    circuit for doors to connect them to one or multiple buttons
    """
    buttons: list



class Door(Wall, Doorcircuit):
    """
    doors are closed until at least one of the via circuit connected buttons is pressed
    """
    pass

if __name__ == '__main__':
    Box1 = Box(0, 10, 20, 0)
    print('hello')