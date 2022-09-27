from abc import ABC, abstractmethod

import numpy as np

import scioi_py_core.core as core

from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid


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

    def __init__(self, length, width, height, position, *args, **kwargs):
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


# ----------------------------------------------- Babylon Objects ------------------------------------------------------
class BabylonObject(ABC):
    """
    - class used whenever the object is supposed to be displayed in Babylon
    - adds itself depending on the object type to the list according to its type
    - contains the name of the texture file used for the object
    """

    def __init__(self, world: EnvironmentDavid, texture_file: str = 'dark'):
        print('initializing Babylon Object')
        assert isinstance(world, EnvironmentDavid)
        # environment where object is supposed to be displayed
        self.babylon_env = world.babylon_env
        # texture the object is supposed to have
        self.texture_file = texture_file
        # add the object to the babylon env list
        self.add_to_babylon_list()

    @abstractmethod
    def add_to_babylon_list(self):
        """
        adds the object to the correspondant list of the babylon environment, has to be defined for each type of object
        """
        pass


class BabylonObstacle(SimpleXYZRObstacle, BabylonObject):
    """
    Obstacle class for obstacles that are supposed to be displayed in Babylon
    """

    def __init__(self, length, width, height, position, *args, **kwargs):
        super().__init__(self, length, width, height, position, *args, **kwargs)

    def add_to_babylon_list(self):
        self.babylon_env.obstacles.append(self)


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
    creates a floor Tile for the Testbed
    """

    # todo: should a floor tile even be collidable? even relevant?

    def __init__(self, length, width, height, position, world: EnvironmentDavid, *args, **kwargs):
        babylon_env_list = world.babylon_env.floortiles
        super().__init__(self, length, width, height, position, babylon_env_list * args, **kwargs)


class CreateTestbedFloor:
    """
    Creates all the Testbed Floortiles
    """

    def __init__(self):
        pass


class CreateBabylonBasicEnvironment:
    """
    creates the Basic Babylon environment with floor Tiles and Border walls on each side
    """
    pass
