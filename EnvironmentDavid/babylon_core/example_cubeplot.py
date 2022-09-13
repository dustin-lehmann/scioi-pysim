import numpy as np
import qmt
import math

from matplotlib import pyplot as plt

from CubePlot import CubePlot


def main():
    R1 = qmt.quatToRotMat(qmt.quatFromAngleAxis(angle=1 / 4 * math.pi, axis=[1, 1, 1]))
    cb1 = CubePlot(dimensions=[3, 2, 1], position=[0, 0, 0], orientation=R1, color=[0, 1, 0])

    R2 = qmt.quatToRotMat(qmt.quatFromAngleAxis(angle=0.67 * math.pi, axis=[1, 0, 0]))
    cb2 = CubePlot(dimensions=[3, 2, 1], position=[1, 1, 2], orientation=R2, color=[0, 0, 1])

    plt.figure()
    plt.subplot(111, projection='3d')
    ax = plt.gca()
    ax.set_box_aspect([1, 1, 1])

    cb1.plot(ax=ax)
    cb2.plot(ax=ax)
    ax.set_xlim([-4, 4])
    ax.set_ylim([-4, 4])
    ax.set_zlim([-4, 4])
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')

    plt.show()


if __name__ == '__main__':
    main()
