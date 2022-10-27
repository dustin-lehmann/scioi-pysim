import numpy as np
import qmt
import math
from scioi_py_core.utils.plot import plot_3d_vectors

from matplotlib import pyplot as plt


class Box:
    center: np.ndarray
    size_x: float
    size_y: float
    height: float
    _angles: [float, float, float]

    visible: bool
    name: str

    def __init__(self, center, size_x, size_y, angles: [float, float, float], size_z: float = 100,
                 edge_discretization=100, visible: bool = True):
        self.center = np.asarray(center)
        self.size = [size_x, size_y, size_z]
        self._angles = np.asarray(angles)
        self.edge_discretization = edge_discretization  # todo: possiblity of equal abstand und anzahl!!!
        self.visible = visible

    @property
    def get_R(self):
        """
        get Rotation matrix based of angles of box
        :return: Rotation Matrix
        """
        quats = qmt.quatFromEulerAngles(self._angles)
        R = qmt.quatToRotMat(quats)
        return R

    def get_vertices(self):
        """
        get the vertices of the box
        :return: list with all 8 vertices
        """
        vertices = []
        for x in [1, -1]:
            for y in [1, -1]:
                for z in [1, -1]:
                    point = self.get_R @ np.asarray(
                        [x * self.size[0] / 2, y * self.size[1] / 2, z * self.size[2] / 2]) + self.center
                    vertices.append(point)
        return vertices

    def get_edge_points(self):
        """
        get multiple points of each edge of the box, how many depends on selected discretization -> total 16 edges
        :return: arrays for each edge point
        """
        edge_points = []
        # x-/ y-pane
        for i in range(0, self.edge_discretization):
            for x in [1, -1]:
                for y in [1, -1]:
                    for z in [1, -1]:
                        # front-/back- -right/ -left
                        fb_rl = np.array(
                            [x * (self.size[0] / 2), y * self.size[1] / 2 * (i / self.edge_discretization),
                             z * self.size[2] / 2])
                        edge_points.append(self.get_R @ fb_rl + self.center)

                        # right-/left- -front/-back
                        rl_fb = np.array(
                            [(x * self.size[0] / 2) * (i / self.edge_discretization), y * self.size[1] / 2,
                             z * self.size[2] / 2])
                        edge_points.append(self.get_R @ rl_fb + self.center)

                        # z -discretization
                        edges = [x * self.size[0] / 2, y * self.size[1] / 2,
                                 (z * self.size[2] / 2) * (i / self.edge_discretization)]
                        edge_points.append(self.get_R @ edges + self.center)

        # z-pane
        return edge_points

    # def collision(self, other: 'Box'):
    #     """
    #     check for collision
    #     - detect collided points
    #     - get min and max collision angle from those points for each axis
    #     - prohibit movement and rotation according to those angles
    #     :param other:
    #     :return:
    #     """
    #     collided_points = self.detect_collided_points(other)
    #     self.get_angle(collided_points)

    def detect_collided_points(self, other: 'Box'):
        """
        detect all collided points between the object and another box
        :param other: other box with which collision is to be checked with
        :return: collided points
        """
        collided_points = []
        R_T_other = other.get_R.T
        edge_points = self.get_edge_points()
        for point in edge_points:
            # relative vector for each point to the center of the other rectangle
            vec_rel = point - other.center
            # rotate the vector according to the other box's R
            vec_rel_trans = R_T_other @ vec_rel
            if abs(vec_rel_trans[0]) <= other.size[0] / 2 and abs(vec_rel_trans[1]) <= other.size[1] / 2 and abs(
                    vec_rel_trans[2]) <= other.size[2] / 2:
                collided_points.append(point)

        return collided_points

    def get_angle(self, vector: list[int], axis='xyz', debug=None, ax=None):
        """
        calculate an angle between a given vector and one or multiple axes
        :param vector: vector
        :param axis: axis to which the angle should be calculated
        :param debug: enable/ disable debugging which returns the vectors that are used to determine the angle as well
        :param ax: axis for plotting, ONLY used for debugging
        :return: angle for the given axis or list of angles for all 3 axes if axis = xyz
        """

        if axis == 'x':
            # vector of x-axis
            vec_axis = [0, 0, 1]
            # vector_axis_x = [self.center[0], self.center[1], 1]
            # vector of which the angle to the x-axis is to be calculated
            vec_point = [0, vector[1], vector[2]]
            angle = math.degrees(qmt.angleBetween2Vecs(vec_axis, vec_point))
            # if debug == 'x' or debug == 'xyz':
            if debug in ['x', 'xyz']:
                # if debug is True:
                print('plotting x ')
                plot_3d_vectors(vec_axis, ax)
                plot_3d_vectors(vec_point, ax)

        elif axis == 'y':
            # vector of y-axis
            # vector_axis_y = [self.center[0], self.center[1], 1]
            vec_axis = [0, 0, 1]
            # vector of which the angle to the y-axis is to be calculated
            vec_point = [vector[0], 0, vector[2]]
            angle = math.degrees(qmt.angleBetween2Vecs(vec_axis, vec_point))
            # if debug == 'y' or debug == 'xyz':
            if debug in ['y', 'xyz']:
                plot_3d_vectors(vec_axis, ax)
                plot_3d_vectors(vec_point, ax)

        elif axis == 'z':
            # vector of z-axis
            # vector_axis_z = [self.center[0], 1, self.center[2]]
            vec_axis = [0, 1, 0]
            # vector of which the angle to the z-axis is to be calculated
            vec_point = [vector[0], vector[1], 0]
            angle = math.degrees(qmt.angleBetween2Vecs(vec_axis, vec_point))
            if debug in ['z','xyz']:
                plot_3d_vectors(vec_axis, ax)
                plot_3d_vectors(vec_point, ax)

        elif axis == 'xyz':
            # calculate angle to all 3 axes
            angle = [self.get_angle(vector, 'x', debug, ax), self.get_angle(vector, 'y', debug, ax),
                     self.get_angle(vector, 'z', debug, ax)]

        else:
            raise ValueError

        return angle

    def get_min_max_angle(self, points: list, axis='xyz', debug=False, ax=None):
        """
        calculate min and max angle for each axis
        - vectors are created from the initial point (center) of the box to each specific point
        - angles for all
        :param points: collided points
        :param axis: determines axis/ axes to get angles for
        :param debug: enabling debug plots the vectors for angel determining
        :param ax: axis for plotting ONLY used for debugging
        :return: list of max and min angles [x,y,z]
        """

        max_angles = [None, None, None]
        min_angles = [None, None, None]

        for point in points:
            # create vector from initial point to input point (terminal point)
            vector = self.center + point
            # calculate angle for each axis (x,y,z)
            angle = self.get_angle(vector, debug=debug, ax=ax)

            for index, x in enumerate(angle):
                index = index
                if max_angles[index] is not None:
                    if angle[index] > max_angles[index]:
                        max_angles[index] = angle[index]
                    if angle[index] < min_angles[index]:
                        min_angles[index] = angle[index]
                else:
                    max_angles[index] = angle[index]
                    min_angles[index] = angle[index]

        print(max_angles)
        print(min_angles)
        return max_angles, min_angles
