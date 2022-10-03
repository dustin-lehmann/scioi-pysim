from abc import ABC, abstractmethod

import numpy as np

import scioi_py_core.core as core

from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid, BabylonVisualization


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
        super().__init__(tilesize, tilesize, height, position)


# ----------------------------------------------- Babylon Objects ------------------------------------------------------
class BabylonObject:
    """
    - class used whenever the object is supposed to be displayed in Babylon
    - adds itself depending on the object type to the list according to its type
    - contains the name of the texture file used for the object, default is the dark texture
    """
    # list where objects of the same type are stored
    babylon_list: list
    # name of file that is used for babylon texture
    texture_file: str
    # object type, parameter that helps for distinction between objects
    type: str

    def __init__(self, babylon_list: list, texture_file: str = 'dark', *args, **kwargs):
        print('initializing Babylon Object!')
        # texture the object is supposed to have
        self.texture_file = texture_file
        self.type = 'obstacle'
        # list with the right kind of objects
        self.babylon_list = babylon_list  # todo: das muss doch nicht per parameter übergeben werden, hier kann man ja einfach auf self zurückgreifen
        # add the object to the babylon env list
        self._add_to_babylon_list()

    def _add_to_babylon_list(self):
        """
        adds the object to the correspondant list of the babylon environment, has to be defined for each type of object
        """
        if self.babylon_list is not None:
            self.babylon_list.append(self)

        else:
            raise Exception('no babylon list to add object to given!')


class BabylonObstacle(BabylonObject, SimpleXYZRObstacle):
    """
    Obstacle class for obstacles that are supposed to be displayed in Babylon
    """
    # list of babylon environment
    babylon_list: list
    # filepath for texture in babylon visualization
    texture_path: str

    def __init__(self, babylon_env: BabylonVisualization, *args, **kwargs):
        # set babylon list to list of obstacles
        print(BabylonObstacle.mro())
        self.babylon_list = babylon_env.obstacles
        # set the texture for obsatcles # todo
        self.texture = None
        # super().__init__(babylon_list=self.babylon_list, texture_file=self.texture, *args, **kwargs)
        SimpleXYZRObstacle.__init__(self, *args, **kwargs)
        BabylonObject.__init__(self, babylon_list=self.babylon_list, texture_file=self.texture, *args, **kwargs)


class BabylonFloorTile(FloorTile, BabylonObject):
    def __init__(self, tilesize, position, babylon_env: BabylonVisualization, *args, **kwargs):
        self.babylon_list = babylon_env.floortiles_list
        FloorTile.__init__(self, tilesize, position, *args, **kwargs)
        BabylonObject.__init__(self, self.babylon_list)


class BabylonSimpleFloor:
    """
    creates the Floor consisting of Tiles according to the number and size specified for the environment
    """

    def __init__(self, testbed_env: EnvironmentDavid, *args, **kwargs):
        for x in range(0, testbed_env.tiles_x):
            for y in range(0, testbed_env.tiles_y):  # todo pass the baxlon env
                tile = BabylonFloorTile(babylon_env=testbed_env.babylon_env,
                                        position=[testbed_env.tile_size / 2 + x * testbed_env.tile_size,
                                                  testbed_env.tile_size / 2 + y * testbed_env.tile_size],
                                        tilesize=testbed_env.tile_size, world=testbed_env.world)


class BabylonWall(BabylonObstacle):

    def __init__(self, length, width, height, position, world: EnvironmentDavid, *args, **kwargs):
        self.babylon_env_list = world.babylon_env.walls
        super().__init__(self, length, width, height, position, world, *args, **kwargs)


class WallsFromTiles(BabylonWall):
    """
    class that creates wall obstacles which position depends on the given Tile
    """

    def __init__(self):
        pass


class FloorTile(BabylonObstacle):
    """
    creates a  square floor Tile for the Testbed
    """

    # todo: should a floor tile even be collidable? even relevant since its beneath robot anyways?

    def __init__(self, tilesize, position, env: EnvironmentDavid, *args, **kwargs):
        height = 1
        babylon_env_list = env.babylon_env.floortiles_list
        super().__init__(self, tilesize, tilesize, height, position, babylon_env_list * args, **kwargs)


class CreateBabylonBasicEnvironment:
    """
    creates the Basic Babylon environment with floor Tiles and Border walls on each side
    """
    pass
