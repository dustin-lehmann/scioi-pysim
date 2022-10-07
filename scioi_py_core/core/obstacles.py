from abc import ABC, abstractmethod

import numpy as np

import scioi_py_core.core as core


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

    def __init__(self, length: float, width: float, height: float, position, visible=True, *args, **kwargs):
        super().__init__(*args, **kwargs)

        position = position

        self.configuration['x'] = position[0]
        self.configuration['y'] = position[1]
        self.configuration['z'] = position[2]
        self.configuration['rot'] = np.eye(3)

        self.physics = core.physics.CuboidPhysics(length=length, width=width, height=height, position=position,
                                                  orientation=np.eye(3))

        self.type = 'obstacle'
        self.visible = visible

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, state: bool):
        self._visible = state
        # add object to sample

    def action_physics_update(self, config, *args, **kwargs):
        self.physics.update(position=[self.configuration['x'], self.configuration['y'], self.configuration['z']],
                            orientation=np.eye(3))


class FloorTile(SimpleXYZRObstacle):
    """
    create a square floor tile, size depending on how many tiles exist in Testbed and its general measurements
    """

    def __init__(self, position, tilesize, height: float = 0.001, *args, **kwargs):
        self.type = 'floor'
        # set z-coordinate of tile to actual floor level
        position[2] = -height / 2

        super().__init__(length=tilesize, width=tilesize, height=height, position=position, visible= True, *args, **kwargs)


class TestbedFloor:
    """
    creates the Floor consisting of Tiles according to the number and size specified for the environment
    """

    def __init__(self, env, *args, **kwargs):
        for x in range(0, env.tiles_x):
            for y in range(0, env.tiles_y):  # todo pass the baxlon env
                # tile = FloorTile(name=f'Floor {x}_{y}',position=[env.tile_size / 2 + x * env.tile_size,
                #                            env.tile_size / 2 + y * env.tile_size, 0],
                #                  tilesize=env.tile_size, *args, **kwargs)
                # position = [env.tile_size['x'] / 2 + x * env.tile_size['x'], env.tile_size['y'] / 2 + y * env.tile_size['y'], 0]
                position = [0.283 / 2 + x * 0.283,
                            0.283 / 2 + y * 0.283, 0]
                tile = FloorTile(name=f'Floor {x}_{y}', position=position,
                                 tilesize=env.tile_size, *args, **kwargs)
