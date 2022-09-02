"""
this pyhton file contains functions that can be used for plotting
- 2d boxes
- 3d boxes
- single points
- vectors
"""

import matplotlib.pyplot as plt
import numpy as np
import qmt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class CubePlot:
    ax: plt.Axes

    dim_x: float
    dim_y: float
    dim_z: float

    position: list
    orientation: np.ndarray

    points: list

    def __init__(self, dimensions, position, orientation, color=None, alpha=0.5, ax=None):
        self.position = position
        self.orientation = orientation
        self.dim_x = dimensions[0]
        self.dim_y = dimensions[1]
        self.dim_z = dimensions[2]
        self.ax = ax
        self.alpha = alpha

        if color is None:
            self.color = 'teal'
        else:
            self.color = color

        self.points_intrinsic = np.array([
            [-self.dim_x / 2, self.dim_y / 2, -self.dim_z / 2],
            [-self.dim_x / 2, -self.dim_y / 2, -self.dim_z / 2],
            [-self.dim_x / 2, -self.dim_y / 2, self.dim_z / 2],
            [-self.dim_x / 2, self.dim_y / 2, self.dim_z / 2],
            [self.dim_x / 2, self.dim_y / 2, -self.dim_z / 2],
            [self.dim_x / 2, -self.dim_y / 2, -self.dim_z / 2],
            [self.dim_x / 2, -self.dim_y / 2, self.dim_z / 2],
            [self.dim_x / 2, self.dim_y / 2, self.dim_z / 2],
        ])

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = np.asarray(value)

    def calc_points(self):
        points_global = []
        for point in self.points_intrinsic:
            point_global = self.position + self.orientation @ point
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

    def plot(self, ax=None):
        if self.ax is None and ax is None:
            raise Exception

        if ax is None:
            ax = self.ax

        faces = self._get_faces(self.calc_points())

        collection = Poly3DCollection(faces, alpha=self.alpha, edgecolor='k', facecolor=self.color)
        ax.add_collection(collection)
        ax.plot3D(self.position[0], self.position[1], self.position[2], markerfacecolor=self.color, markeredgecolor='k',
                  marker='o', markersize=5, alpha=1)


class CubePlotBox(CubePlot):
    """
    Wrapper for CubePlot to be able to directly plot boxes
    """

    def __init__(self, dimensions: list, position: list, orientation: list, colour, ax):
        super().__init__(dimensions=[dimensions[0], dimensions[1], dimensions[2]],
                         position=[position[0], position[1], position[2]],
                         orientation=orientation,
                         color=colour)
        self.plot(ax)


def plot_points(np_point_array, ax: plt.gca, color='red'):
    if type(np_point_array) is not np.array:
        np_point_array = np.asarray(np_point_array)
    ax.scatter(np_point_array[:, 0], np_point_array[:, 1], np_point_array[:, 2], color=color)


def plot_3d_vectors(vector, ax, origin=None):
    """
    plot a vector via matplotlib
    :param ax:
    :param vector: vector that is going to be plotted
    :param origin: origin for vector
    :return: nothing
    """
    vector = qmt.normalized(vector)
    # set vector origin
    if origin is None:
        origin = [0, 0, 0]
    # create vector
    ax.quiver(origin[0], origin[1], origin[2], vector[0], vector[1], vector[2])
