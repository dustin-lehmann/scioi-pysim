import numpy as np
import qmt
import math

from matplotlib import pyplot as plt

from CubePlot import CubePlot


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
        self.edge_discretization = edge_discretization  # todo: possibility of equal abstand und anzahl
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

    def collision(self, other: 'Box'):
        """
        :param other: other box with which collision is to be checked with
        :return:
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

    def get_angles(self, points):
        max_angles = [0, 0, 0]
        min_angles = [0, 0, 0]
        for point in points:
            angle = [0, 0, 0]
            # x_axis -> phi
            # angle[0] = math.degrees(qmt.angleBetween2Vecs([1, 0, 0], 0, point[1], point[2]))
            # #  y_axis-> theta
            # angle[1] = math.degrees(qmt.angleBetween2Vecs([0, 0, 1], [point[0], 0, point[2]]))
            # z_axis -> psi
            angle[2] = math.degrees(qmt.angleBetween2Vecs([0, 1, 0], [point[0], point[1], 0]))
            print("angle x: {}, angle y: {}, angle z: {}".format(angle[0], angle[1], angle[2]))

            for index, x in enumerate(angle):
                index = index
                if angle[index] > max_angles[index]:
                    max_angles[index] = angle[index]
                if angle[index] < min_angles[index]:
                    min_angles[index] = angle[index]
        pass


class CubePlotBox(CubePlot):
    """
    Wrapper for CubePlot to be able to directly plot boxes
    """

    def __init__(self, box: Box, colour, ax):
        super().__init__(dimensions=[box.size[0], box.size[1], box.size[2]],
                         position=[box.center[0], box.center[1], box.center[2]],
                         orientation=box.get_R,
                         color=colour)
        self.plot(ax)


def plot_points(np_point_array, color='red'):
    if type(np_point_array) is not np.array:
        np_point_array = np.asarray(np_point_array)
    ax.scatter(np_point_array[:, 0], np_point_array[:, 1], np_point_array[:, 2], color=color)


if __name__ == '__main__':
    plt.figure()
    plt.subplot(111, projection='3d')
    ax = plt.gca()
    ax.set_box_aspect([1, 1, 1])

    # Box1
    Box1 = Box(center=[0, 0, 0], size_x=3, size_y=2, size_z=1,
               angles=(math.radians(20), math.radians(45), math.radians(0)))
    # cpb1 = CubePlotBox(Box1, [0, 0, 1], ax)

    # Box2
    Box2 = Box(center=[1, 1, 1], size_x=3, size_y=2, size_z=1, angles=(0, 0, 0))
    # cpb2 = CubePlotBox(Box2, [0, 1, 0], ax)

    origin = [0, 0, 0]
    test_points = [[1, 0, 0]]
    Box1.get_angles(test_points)

    # # collision
    # plot_points(Box1.collision(Box2))
    # plot_points(Box2.collision(Box1))

    limitations = [-2, 2]
    ax.set_xlim([limitations[0], limitations[1]])
    ax.set_ylim([limitations[0], limitations[1]])
    ax.set_zlim([limitations[0], limitations[1]])
    ax.quiver(origin[0], origin[1], origin[2], test_points[0][0], test_points[0][1], test_points[0][1])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    plt.show()

    print('hello')
