from matplotlib import pyplot as plt

from scioi_py_core.core.physics import SpherePrimitive, PhysicsSpherePlot


def main():
    sphere = SpherePrimitive(radius=2, position=[0, 0, 10])



    PhysicsSpherePlot(ax=ax, sphere=sphere)

    plt.show()


if __name__ == '__main__':
    main()
