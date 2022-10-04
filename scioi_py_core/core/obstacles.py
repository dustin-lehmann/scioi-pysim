from abc import ABC, abstractmethod

import numpy as np

import scioi_py_core.core as core

# from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid, BabylonVisualization


# from EnvironmentDavid.Tests.Test_Environment import EnvironmentDavid_thisExample


class Obstacle(core.world.WorldObject, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collision.settings.check = False


# ======================================================================================================================
class SimpleXYZRObstacle(Obstacle):
    """
    Simple Basis for obstacles used in Simulation
    """
    physics: core.physics.CuboidPhysics

    def __init__(self, length: float, width: float, height: float, position, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configuration['x'] = position[0]
        self.configuration['y'] = position[1]
        self.configuration['z'] = position[2]
        self.configuration['rot'] = np.eye(3)

        self.physics = core.physics.CuboidPhysics(length=length, width=width, height=height, position=position,
                                                  orientation=np.eye(3))

        self.type = 'obstacle'

    def action_physics_update(self, config, *args, **kwargs):
        self.physics.update(position=[self.configuration['x'], self.configuration['y'], self.configuration['z']],
                            orientation=np.eye(3))


class SimpleWall(SimpleXYZRObstacle):
    pass


class FloorTile(SimpleXYZRObstacle):
    """
    create a square floor tile depending on how many tiles exist in Testbed and what the size of it is going to be
    """

    def __init__(self, tilesize, position, height: float = 0.001, *args, **kwargs):
        self.type = 'floor'
        super().__init__(tilesize, tilesize, height, position)

# class BabylonSimpleFloor:
#     """
#     creates the Floor consisting of Tiles according to the number and size specified for the environment
#     """
#
#     def __init__(self, *args, **kwargs):
#         for x in range(0, testbed_env.tiles_x):
#             for y in range(0, testbed_env.tiles_y):  # todo pass the baxlon env
#                 tile = BabylonFloorTile(babylon_env=testbed_env.babylon_env,
#                                         position=[testbed_env.tile_size / 2 + x * testbed_env.tile_size,
#                                                   testbed_env.tile_size / 2 + y * testbed_env.tile_size],
#                                         tilesize=testbed_env.tile_size, world=testbed_env.world)


class SimpleObstacle(SimpleXYZRObstacle):
    """
    Obstacle class for obstacles that are supposed to be displayed in Babylon
    """
    # filepath for texture in babylon visualization
    texture_path: str

    obstacle: SimpleXYZRObstacle

    def __init__(self, *args, **kwargs):
        # set babylon list to list of obstacles

        # set the texture for obsatcles # todo
        self.texture = None
        super().__init__(*args, **kwargs)


# class SimpleWall(SimpleObstacle):
#
#     def __init__(self, length, width, height, position, world: EnvironmentDavid, *args, **kwargs):
#         self.babylon_env_list = world.babylon_env.walls
#         super().__init__(self, length, width, height, position, world, *args, **kwargs)


class WallsFromTiles(SimpleWall):
    """
    class that creates wall obstacles which position depends on the given Tile
    """

    def __init__(self):
        pass


# class FloorTile(SimpleObstacle):
#     """
#     creates a  square floor Tile for the Testbed
#     """
#
#     # todo: should a floor tile even be collidable? even relevant since its beneath robot anyways?
#
#     def __init__(self, tilesize, position, env: EnvironmentDavid, *args, **kwargs):
#         height = 1
#         babylon_env_list = env.babylon_env.floortiles_list
#         super().__init__(self, tilesize, tilesize, height, position, babylon_env_list * args, **kwargs)


class CreateBabylonBasicEnvironment:
    """
    creates the Basic Babylon environment with floor Tiles and Border walls on each side
    """
    pass
