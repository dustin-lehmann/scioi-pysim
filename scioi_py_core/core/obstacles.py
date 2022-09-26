from abc import ABC

import numpy as np

import scioi_py_core.core as core


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
    texture: str = ''
    def __init__(self, length, width, height, position, *args, **kwargs):
        super().__init__(self, length, width, height, position, *args, **kwargs)


class Walls(SimpleXYZRObstacle):
    texture: str = ''
    def __init__(self, length, width, height, position, *args, **kwargs):
        super().__init__(self, length, width, height, position, *args, **kwargs)

class Floor(SimpleXYZRObstacle):
    texture: str = ''
    def __init__(self, length, width, height, position, *args, **kwargs):
        super().__init__(self, length, width, height, position, *args, **kwargs)