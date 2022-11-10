import copy
import dataclasses
from abc import ABC, abstractmethod
from typing import Union

import numpy as np
from matplotlib import pyplot, pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from scioi_py_core.core import spaces


# ======================================================================================================================

class ObjectPrimitive(ABC):
    collision: dataclasses.dataclass
    pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def collision(self, object: 'ObjectPrimitive'):
        pass


# ----------------------------------------------------------------------------------------------------------------------
def collisionCuboidCuboid(cuboid1: 'CuboidPrimitive', cuboid2: 'CuboidPrimitive'):
    collided_points_1 = []
    collided_points_2 = []

    R_T = cuboid1.orientation.T
    for point in cuboid2.points_global:
        vec_rel_global = point - cuboid1.position
        vec_rel_local = R_T @ vec_rel_global

        if abs(vec_rel_local[0]) <= cuboid1.size[0] / 2 and abs(vec_rel_local[1]) <= cuboid1.size[1] / 2 and abs(
                vec_rel_local[2]) <= cuboid1.size[2] / 2:
            collided_points_1.append(point)

    if len(collided_points_1) > 0:
        return True

    R_T_2 = cuboid2.orientation.T
    for point in cuboid1.points_global:
        vec_rel_global = point - cuboid2.position
        vec_rel_local = R_T_2 @ vec_rel_global

        if abs(vec_rel_local[0]) <= cuboid2.size[0] / 2 and abs(vec_rel_local[1]) <= cuboid2.size[1] / 2 and abs(
                vec_rel_local[2]) <= cuboid2.size[2] / 2:
            collided_points_2.append(point)
    if len(collided_points_2) > 0:
        return True

    return False


def collisionCuboidSphere(cuboid: 'CuboidPrimitive', sphere: 'SpherePrimitive'):
    print('the collision of cuboid and sphere has not been implemented yet! ')
    pass


# ----------------------------------------------------------------------------------------------------------------------
def collisionSphereSphere(sphere1: 'SpherePrimitive', sphere2: 'SpherePrimitive'):
    distance = np.linalg.norm(sphere2.position - sphere1.position) - sphere1.radius - sphere2.radius
    if distance <= 0:
        return True

    else:
        return False


# ======================================================================================================================
@dataclasses.dataclass
class CuboidCollisionData:
    collision_state: bool = False
    collision_points: list = dataclasses.field(default_factory=list)
    collision_areas: dict = dataclasses.field(default_factory=dict)


class CuboidPrimitive(ObjectPrimitive):
    size: list[float]
    position: np.ndarray
    orientation: np.ndarray

    points_local: list[np.ndarray]
    points_global: list[np.ndarray]

    discretization: Union[float, int]
    discretization_type: str  # 'spacing', 'number'
    collision: CuboidCollisionData = CuboidCollisionData()

    def __init__(self, size: list, position: Union[np.ndarray, list] = None, orientation: np.ndarray = None,
                 discretization_type: str = 'number', discretization: Union[int, float] = 10):
        self.size = size
        self.position = position
        self.orientation = orientation
        self.discretization_type = discretization_type
        self.discretization = discretization

        self._calcPointsIntrinsic(self.discretization, self.discretization_type)
        self.points_global = copy.copy(self.points_local)
        self._updatePointsGlobal()

    # === METHODS ======================================================================================================
    def update(self, position: np.ndarray, orientation: np.ndarray, *args, **kwargs):
        """
        Updates the state of the Cuboid and recalculates the global points for collision detection
        :param position:
        :param orientation:
        :param args:
        :param kwargs:
        :return:
        """
        assert(isinstance(position, np.ndarray))
        assert (isinstance(orientation, np.ndarray))

        if isinstance(position, list):
            position = np.asarray(position)

        self.position = position
        self.orientation = orientation
        self._updatePointsGlobal()

    # ------------------------------------------------------------------------------------------------------------------
    def collision(self, object: ObjectPrimitive):

        if isinstance(object, CuboidPrimitive):
            return collisionCuboidCuboid(self, object)

        if isinstance(object, CylinderPrimitive):
            pass

        if isinstance(object, SpherePrimitive):
            pass

    def getDiagonal(self):
        return np.sqrt(self.size[0] ** 2 + self.size[1] ** 2 + self.size[2] ** 2)

    # === PRIVATE METHODS ==============================================================================================
    def _calcPointsIntrinsic(self, discretization, discretization_type):
        # Determine the vertices
        vertices = []
        self.points_local = []
        for x in [1, -1]:
            for y in [1, -1]:
                for z in [1, -1]:
                    point = np.asarray(
                        [x * self.size[0] / 2, y * self.size[1] / 2, z * self.size[2] / 2])
                    vertices.append(point)
                    self.points_local.append(point)

        # Get the Edge Points
        # x-/ y-pane
        for i in range(0, self.discretization):
            for x in [1, -1]:
                for y in [1, -1]:
                    for z in [1, -1]:
                        # front-/back- -right/ -left
                        fb_rl = np.array(
                            [x * (self.size[0] / 2), y * self.size[1] / 2 * (i / self.discretization),
                             z * self.size[2] / 2])
                        self.points_local.append(fb_rl)

                        # right-/left- -front/-back
                        rl_fb = np.array(
                            [(x * self.size[0] / 2) * (i / self.discretization), y * self.size[1] / 2,
                             z * self.size[2] / 2])
                        self.points_local.append(rl_fb)

                        # z -discretization
                        edges = np.array([x * self.size[0] / 2, y * self.size[1] / 2,
                                          (z * self.size[2] / 2) * (i / self.discretization)])
                        self.points_local.append(edges)

    def _updatePointsGlobal(self):
        for i, point in enumerate(self.points_local):
            self.points_global[i] = self.orientation @ point + self.position


# ======================================================================================================================
class CylinderPrimitive(ObjectPrimitive):
    def update(self, *args, **kwargs):
        pass

    def collision(self, object: ObjectPrimitive):

        if isinstance(object, CuboidPrimitive):
            pass

        if isinstance(object, CylinderPrimitive):
            pass

        if isinstance(object, SpherePrimitive):
            pass


# ======================================================================================================================
class SpherePrimitive(ObjectPrimitive):
    radius: float
    position: np.ndarray

    def __init__(self, radius: float, position=None):
        self.radius = radius

        if position is None:
            position = [0, 0, 0]

        self.position = position

    # === PROPERTIES ===================================================================================================
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        if isinstance(value, list):
            value = np.asarray(value)
        self._position = value

    # === METHODS ======================================================================================================
    def update(self, position, *args, **kwargs):
        """

        :param position:
        :param args:
        :param kwargs:
        :return:
        """

        self.position = position

    def collision(self, object: ObjectPrimitive):

        if isinstance(object, CuboidPrimitive):
            pass

        if isinstance(object, CylinderPrimitive):
            pass

        if isinstance(object, SpherePrimitive):
            return collisionSphereSphere(self, object)


# ======================================================================================================================
@dataclasses.dataclass
class PhysicalBodyCollisionData:
    collision_state: bool = False
    collided_primitives: list = dataclasses.field(default_factory=list)


class PhysicalBody(ABC):
    bounding_objects: dict[str, ObjectPrimitive]
    proximity_sphere: SpherePrimitive
    collision: PhysicalBodyCollisionData
    configuration: spaces.State

    def __init__(self):
        self.proximity_sphere = SpherePrimitive(radius=-1)
        self.collision = PhysicalBodyCollisionData()

    # === METHODS ======================================================================================================
    def collisionCheck(self, other: 'PhysicalBody'):
        # Check if the two physical objects are close enough to collide by doing a proximity sphere check
        if self.proximity_sphere.radius > 0 and other.proximity_sphere.radius > 0 and \
                not self.proximity_sphere.collision(other.proximity_sphere):
            return False

        # Go through all objects and check for collision TODO: Add more output than boolean
        collision = False
        for _, obj in self.bounding_objects.items():
            for _, obj_other in other.bounding_objects.items():
                collision = collision or obj.collision(obj_other)

        if collision:
            self.collision.collision_state = True
        else:
            self.collision.collision_state = False

        return collision

    # ------------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def update(self, *args, **kwargs):
        """
        This function needs to be overwritten for individual representations to account for offsets between individual
        objects
        :param args:
        :param kwargs:
        :return:
        """
        pass

    # === PRIVATE METHODS ==============================================================================================
    @abstractmethod
    def _calcProximitySphere(self):
        """
        Calculates the proximity sphere for collision detection
        :return:
        """
        # TODO
        ...

    @abstractmethod
    def _getProximitySphereRadius(self):
        ...


# ======================================================================================================================
class CuboidPhysics(PhysicalBody):
    def __init__(self, size_x, size_y, size_z, position, orientation):
        super().__init__()
        self.bounding_objects = {
            'cuboid': CuboidPrimitive(size=[size_x, size_y, size_z], position=position, orientation=orientation)
        }

    def update(self, config, *args, **kwargs):
        self.bounding_objects['cuboid'].update(position=config['pos'].value, orientation=config['ori'].value)
        self._calcProximitySphere()

    def _calcProximitySphere(self):
        self.proximity_sphere.radius = self._getProximitySphereRadius()
        self.proximity_sphere.position = self.bounding_objects['cuboid'].position

    def _getProximitySphereRadius(self):
        return self.bounding_objects['cuboid'].getDiagonal() / 2 * 1.1


# ======================================================================================================================
class PhysicsCuboidPlot:
    ax: pyplot.Axes
    cuboid: CuboidPrimitive

    def __init__(self, ax, cuboid: CuboidPrimitive, color: list = None, alpha: float = 0.5,
                 plot_edge_points: bool = False):
        self.cuboid = cuboid
        self.ax = ax

        if color is None:
            color = [0.5, 0.5, 0.5]
        self.color = color

        self.alpha = alpha

        self.points_intrinsic = np.array([
            [-self.cuboid.size[0] / 2, self.cuboid.size[1] / 2, -self.cuboid.size[2] / 2],
            [-self.cuboid.size[0] / 2, -self.cuboid.size[1] / 2, -self.cuboid.size[2] / 2],
            [-self.cuboid.size[0] / 2, -self.cuboid.size[1] / 2, self.cuboid.size[2] / 2],
            [-self.cuboid.size[0] / 2, self.cuboid.size[1] / 2, self.cuboid.size[2] / 2],
            [self.cuboid.size[0] / 2, self.cuboid.size[1] / 2, -self.cuboid.size[2] / 2],
            [self.cuboid.size[0] / 2, -self.cuboid.size[1] / 2, -self.cuboid.size[2] / 2],
            [self.cuboid.size[0] / 2, -self.cuboid.size[1] / 2, self.cuboid.size[2] / 2],
            [self.cuboid.size[0] / 2, self.cuboid.size[1] / 2, self.cuboid.size[2] / 2],
        ])

        if plot_edge_points:
            self._plotEdgePoints()
        self.plot()

    def calc_points(self):
        points_global = []
        for point in self.points_intrinsic:
            point_global = self.cuboid.position + self.cuboid.orientation @ point
            points_global.append(point_global)
        return points_global

    def _get_faces(self, points_global):
        faces = [[points_global[0], points_global[1], points_global[2], points_global[3]],
                 [points_global[1], points_global[5], points_global[6], points_global[2]],
                 [points_global[0], points_global[1], points_global[5], points_global[4]],
                 [points_global[4], points_global[5], points_global[6], points_global[7]],
                 [points_global[3], points_global[2], points_global[6], points_global[7]],
                 [points_global[0], points_global[4], points_global[7], points_global[3]]]
        return faces

    def _plotEdgePoints(self):

        if type(self.cuboid.points_global) is not np.array:
            np_point_array = np.asarray(self.cuboid.points_global)
        else:
            np_point_array = self.cuboid.points_global
        self.ax.scatter(np_point_array[:, 0], np_point_array[:, 1], np_point_array[:, 2], color='red')

    def plot(self, ax=None):
        if self.ax is None and ax is None:
            raise Exception

        if ax is None:
            ax = self.ax

        faces = self._get_faces(self.calc_points())

        collection = Poly3DCollection(faces, alpha=self.alpha, edgecolor='k', facecolor=self.color)
        ax.add_collection(collection)
        ax.plot3D(self.cuboid.position[0], self.cuboid.position[1], self.cuboid.position[2], markerfacecolor=self.color,
                  markeredgecolor='k',
                  marker='o', markersize=5, alpha=1)


class PhysicsSpherePlot:
    ax: pyplot.Axes
    sphere: SpherePrimitive

    def __init__(self, ax, sphere: SpherePrimitive, color: list = None, alpha: float = 0.75):
        self.ax = ax
        self.sphere = sphere

        if color is None:
            color = [0.5, 0.5, 0.5]
        self.color = color
        self.alpha = alpha

        if self.ax is not None:
            self.plot()

    def plot(self, ax=None):
        if self.ax is None and ax is None:
            raise Exception

        if ax is None:
            ax = self.ax

        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)

        x = self.sphere.radius * np.outer(np.cos(u), np.sin(v)) + self.sphere.position[0]
        y = self.sphere.radius * np.outer(np.sin(u), np.sin(v)) + self.sphere.position[1]
        z = self.sphere.radius * np.outer(np.ones(np.size(u)), np.cos(v)) + self.sphere.position[2]
        ax.plot_surface(x, y, z, rstride=5, cstride=5, color=self.color, linewidth=0.5, edgecolor='black',
                        alpha=self.alpha)


class PhysicsCylinderPlot:
    pass


class PhysicsDebugPlot:
    representations: list[PhysicalBody]
    ax: pyplot.Axes

    def __init__(self, representations: list, limits=None, **kwargs):
        pyplot.figure()
        pyplot.subplot(111, projection='3d')
        self.kwargs = kwargs
        self.ax = pyplot.gca()
        ax = pyplot.gca()
        self.representations = representations
        # ax.set_box_aspect([1, 1, 1])
        self.plot()

        if limits is not None:
            if 'x' in limits:
                ax.set_xlim(limits['x'])
            if 'y' in limits:
                ax.set_ylim(limits['y'])
            if 'z' in limits:
                ax.set_zlim(limits['z'])

        len_x = abs(ax.get_xlim()[1] - ax.get_xlim()[0])
        len_y = abs(ax.get_ylim()[1] - ax.get_ylim()[0])
        len_z = abs(ax.get_zlim()[1] - ax.get_zlim()[0])

        ax.set_box_aspect([1, len_y / len_x, len_z / len_x])

        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        pyplot.show()

    def plot(self):
        for body in self.representations:
            # TODO: choose color here
            for name, obj in body.bounding_objects.items():
                if isinstance(obj, SpherePrimitive):
                    PhysicsSpherePlot(ax=self.ax, sphere=obj, **self.kwargs)
                if isinstance(obj, CuboidPrimitive):
                    PhysicsCuboidPlot(ax=self.ax, cuboid=obj, **self.kwargs)
