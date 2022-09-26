from abc import ABC

import numpy as np

import scioi_py_core.core as core

from EnvironmentDavid.babylon_core.babylon_objects import VisulizationEnvironment


class Obstacle(core.world.WorldObject, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collision.settings.check = False


# ======================================================================================================================
class SimpleXYZRObstacle(Obstacle):
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


class BabylonObstacle(SimpleXYZRObstacle):
    """
    Obstacle class for obstacles that are supposed to be displayed in Babylon
    """
    babylon_texture: str = ''

    def __init__(self, length, width, height, position, babylon_env_list: list = None, *args, **kwargs):
        super().__init__(self, length, width, height, position, *args, **kwargs)

        if babylon_env_list is not None:
            # add element to the babylon_env list, to later write the object in the json file for babylon
            babylon_env_list.append(self)


class Wall(BabylonObstacle):

    def __init__(self, length, width, height, position, babylon_env: VisulizationEnvironment, *args, **kwargs):
        babylon_env_list = babylon_env.walls
        super().__init__(self, length, width, height, position, babylon_env_list, *args, **kwargs)


class WallsFromTiles(Wall):
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

    def __init__(self, length, width, height, position, babylon_env: VisulizationEnvironment, *args, **kwargs):
        babylon_env_list = babylon_env.floortiles
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
