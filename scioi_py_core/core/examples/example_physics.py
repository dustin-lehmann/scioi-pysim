import math

import numpy as np
from matplotlib import pyplot as plt

import scioi_py_core.core.physics as physics
from scioi_py_core.utils.orientations import rotmatFromEuler


def example_spheres():
    # Define two spheres
    sphere1 = physics.SpherePrimitive(radius=1, position=[-3, 0, 0])
    sphere2 = physics.SpherePrimitive(radius=2, position=[1.8, -0.2, 0])

    # Check for collision between the two spheres
    collision = sphere1.collision(sphere2)

    # Print the result
    print(f"{collision=}")


def example_representations():
    # Build a simple representation made of two spheres
    class ExampleBody(physics.PhysicalBody):
        """
        The object is made of two spheres. The objects center is the center of the first sphere 2, with the x-axis
        pointing towards the center of sphere 2
        """
        offset: np.ndarray

        def __init__(self, radius1, radius2, offset):
            """

            :param radius1: Radius of the first sphere
            :param radius2: Radius of the second sphere
            :param offset: Offset vector of both spheres
            """
            super().__init__()

            self.bounding_objects = {
                'sphere1': physics.SpherePrimitive(radius=radius1, position=[0, 0, 0]),
                'sphere2': physics.SpherePrimitive(radius=radius2, position=offset)
            }
            self.offset = offset

        def update(self, position, orientation, *args, **kwargs):
            if isinstance(position, list):
                position = np.asarray(position)

            self.bounding_objects['sphere1'].update(position)
            position_sphere_2 = position + orientation @ self.offset
            self.bounding_objects['sphere2'].update(position_sphere_2)

        def _calcProximitySphere(self):
            pass

    # Generate two objects
    body1 = ExampleBody(radius1=1, radius2=0.5, offset=[1.5, 0, 0])
    body2 = ExampleBody(radius1=0.5, radius2=0.25, offset=[.75, 0, 0])

    # Update both objects
    body1.update(position=[1, 0, 0], orientation=rotmatFromEuler(angles=[-math.pi / 4, 0, 0], convention='yxz'))
    body2.update(position=[-0.8, 0, 0], orientation=rotmatFromEuler(angles=[0, 0, 0.9 * math.pi / 4], convention='xyz'))

    # Check for collision between the two bodies
    collision = body1.collisionCheck(body2)
    print(f"{collision=}")

    # Plot both bodies
    physics.PhysicsDebugPlot(representations=[body1, body2])


def example_cuboid():
    ori = rotmatFromEuler(angles=[math.pi/4, math.pi/4, 0], convention='zyx')
    cuboid1 = physics.CuboidPrimitive(size=[1, 1, 1], position=[1, 0, -5], orientation=ori)

    plt.figure()
    plt.subplot(111, projection='3d')
    ax = plt.gca()

    physics.PhysicsCuboidPlot(ax, cuboid1, plot_edge_points=True)
    plt.show()


if __name__ == '__main__':
    # example_spheres()
    # example_representations()
    example_cuboid()
