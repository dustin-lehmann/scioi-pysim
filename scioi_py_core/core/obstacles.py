from abc import ABC, abstractmethod

import numpy as np

import scioi_py_core.core as core

from EnvironmentDavid.Objects.EnvironmentDavid import EnvironmentDavid, BayblonVisualization


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

    def __init__(self, length:float, width:float, height:float, position, *args, **kwargs):
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
class BabylonObject():
    """
    - class used whenever the object is supposed to be displayed in Babylon
    - adds itself depending on the object type to the list according to its type
    - contains the name of the texture file used for the object, default is the dark texture
    """

    def __init__(self, babylon_list: list, texture_file: str = 'dark'):
        print('initializing Babylon Object')
        # texture the object is supposed to have
        self.texture_file = texture_file
        # list with the right kind of objects
        self.babylon_list = None
        # add the object to the babylon env list
        self._add_to_babylon_list()

    def _add_to_babylon_list(self, babylon_list, texture=None):
        """
        adds the object to the correspondant list of the babylon environment, has to be defined for each type of object
        """
        if self.babylon_list is not None:
            self.babylon_list.append()

        else:
            raise Exception('no babylon list to add object to!')


class BabylonObstacle(SimpleXYZRObstacle, BabylonObject):
    """
    Obstacle class for obstacles that are supposed to be displayed in Babylon
    """
    # list of babylon environment
    babylon_list: list
    # filepath for texture in babylon visualizatiobn
    texture_path: str

    def __init__(self, babylon_env: BayblonVisualization , *args, **kwargs):
        # set babylon list to list of obstacles
        self.babylon_list = babylon_env.obstacles
        # set the texture for obsatcles # todo
        self.texture = None
        super().__init__(babylon_list=self.babylon_list, texture_file=self.texture, *args, **kwargs)


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
