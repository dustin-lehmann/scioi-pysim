from abc import ABC, abstractmethod

import numpy as np
from scioi_py_core.utils.orientations import psiFromRotMat
import scioi_py_core.core as core


# from EnvironmentDavid.Tests.Test_Environment import EnvironmentDavid_thisExample


class Obstacle(core.world.WorldObject, ABC):
    object_type = 'obstacle'
    static = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collision.settings.check = False


# ======================================================================================================================
class CuboidObstacle_3D(Obstacle):
    """
    Simple Basis for obstacles used in Simulation
    """
    physics: core.physics.CuboidPhysics
    object_type = 'obstacle'
    size: dict

    def __init__(self, size_x: float, size_y: float, size_z: float, position, orientation=None, visible=True, name=None,
                 world: core.world.World = None, *args,
                 **kwargs):
        # Check if the world space is 3D
        super().__init__(name=name, world=world, *args, **kwargs)
        assert (isinstance(self.world.space, core.spaces.Space3D))

        self.size = {
            'x': size_x,
            'y': size_y,
            'z': size_z
        }

        self.configuration['pos']['x'] = position[0]
        self.configuration['pos']['y'] = position[1]
        self.configuration['pos']['z'] = position[2]

        if orientation is not None:
            self.configuration['ori'] = orientation
        else:
            self.configuration['ori'] = np.eye(3)

        self.physics = core.physics.CuboidPhysics(size_x=size_x, size_y=size_y, size_z=size_z, position=position,
                                                  orientation=self.configuration['ori'].value)
        self.visible = visible

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, state: bool):
        self._visible = state
        # todo: add object to sample

    def _getParameters(self):
        params = super()._getParameters()
        params['size'] = {
            'x': self.size['x'],
            'y': self.size['y'],
            'z': self.size['z'],
        }
        return params

    def _getSample(self):
        sample = super()._getSample()
        return sample

    def _init(self, *args, **kwargs):
        self._updatePhysics()


# class FloorTile(CuboidObstacle_3D):
#     """
#     create a square floor tile, size depending on how many tiles exist in Testbed and its general measurements
#     """
#
#     def __init__(self, position, tilesize, size_z: float = 0.001, *args, **kwargs):
#         # set z-coordinate of tile to actual floor level
#         position[2] = -size_z / 2
#         tilesize_x = tilesize['x']
#         tilesize_y = tilesize['y']
#         super().__init__(size_x=tilesize_y, size_y=tilesize_x, size_z=size_z, position=position, visible=True, *args,
#                          **kwargs)
#         self.type = 'floor_tile'
#
#
# class TestbedFloor:
#     """
#     creates the Floor consisting of Tiles according to the number and size specified for the environment
#     """
#
#     def __init__(self, env, *args, **kwargs):
#         for x in range(0, env.world.tiles_x):
#             for y in range(0, env.world.tiles_y):
#                 # calculate position of next floortile
#                 position = [env.world.tile_size['x'] / 2 + x * env.world.tile_size['x'],
#                             env.world.tile_size['y'] / 2 + y * env.world.tile_size['y'], 0]
#                 # create a new floortile
#                 FloorTile(name=f'Floor {x}_{y}', position=position,
#                           tilesize=env.world.tile_size, *args, **kwargs)
#
#
# class Wall(CuboidObstacle_3D):
#     """
#     create a wall
#     """
#     wall_height: float
#     wall_length: float
#
#     def __init__(self, position: list['float'], lenght: float, size_z: float, *args, **kwargs):
#         wall_thickness = 0.01
#         super().__init__(size_x=lenght, size_y=wall_thickness, size_z=size_z, position=position, visible=True,
#                          *args,
#                          **kwargs)
#         self.type = 'wall'
#
#
# class WallOnTile(Wall):
#     """
#     create a wall horizontal/vertical which is positioned bottom/left
#     """
#
#     def __init__(self, tile, orientation, *args, **kwargs):
#         pass
