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

    def __init__(self, length: float, width: float, height: float, position, visible=True, name=None, world=None, *args,
                 **kwargs):
        super().__init__(name=name, world=world, *args, **kwargs)

        if world is None:
            raise Exception('obstacle has no world!')  # todo: better ways to make sure these params are given?

        if name is None:
            raise Exception('obstacle has no name!')

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
        # todo: add object to sample

    def action_physics_update(self, config, *args, **kwargs):
        self.physics.update(position=[self.configuration['x'], self.configuration['y'], self.configuration['z']],
                            orientation=np.eye(3))


class FloorTile(SimpleXYZRObstacle):
    """
    create a square floor tile, size depending on how many tiles exist in Testbed and its general measurements
    """

    def __init__(self, position, tilesize, height: float = 0.001, *args, **kwargs):
        # set z-coordinate of tile to actual floor level
        position[2] = -height / 2
        tilesize_x = tilesize['x']
        tilesize_y = tilesize['y']
        super().__init__(length=tilesize_y, width=tilesize_x, height=height, position=position, visible=True, *args,
                         **kwargs)
        self.type = 'floor_tile'


class TestbedFloor:
    """
    creates the Floor consisting of Tiles according to the number and size specified for the environment
    """

    def __init__(self, env, *args, **kwargs):
        for x in range(0, env.tiles_x):
            for y in range(0, env.tiles_y):
                # calculate position of next floortile
                position = [env.tile_size['x'] / 2 + x * env.tile_size['x'],
                            env.tile_size['y'] / 2 + y * env.tile_size['y'], 0]
                # create a new floortile
                FloorTile(name=f'Floor {x}_{y}', position=position,
                          tilesize=env.tile_size, *args, **kwargs)


class Wall(SimpleXYZRObstacle):
    """
    create a wall
    """
    wall_height: float
    wall_length: float

    def __init__(self, position: list['float'], lenght: float, height: float, *args, **kwargs):
        wall_thickness = 0.01
        super().__init__(length=lenght, width=wall_thickness, height=height, position=position, visible=True,
                         *args,
                         **kwargs)
        self.type = 'wall'


class WallOnTile(Wall):
    """
    create a wall horizontal/vertical which is positioned bottom/left
    """

    def __init__(self, tile, orientation, *args, **kwargs):
        pass
