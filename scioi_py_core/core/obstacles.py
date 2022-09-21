from abc import ABC

import numpy as np

import scioi_py_core.core as core


class Obstacle(core.world.WorldObject, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.collision.settings.check = False
        # add the new object to the world
        # self.world = world
        # self.world.addObject(self)

        # self.dynamics.state = [0, 0, 0]

    # @property
    # def configuration(self):
    #     return self.spaces.config_space.map([0,0,0])
    #
    # @configuration.setter
    # def configuration(self, value):
    #     raise Exception("Cannot set configuration of obstacle. Set the state instead.")


# ======================================================================================================================
class SimpleXYZRObstacle(Obstacle):
    physics: core.physics.CuboidPhysics

    def __init__(self, length, width, height, position, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.physics = core.physics.CuboidPhysics(length=length, width=width, height=height, position=position,
                                                  orientation=np.eye(3))

    def action_physics_update(self, config, *args, **kwargs):
        self.physics.update(position=[self.configuration['x'], self.configuration['y'], self.configuration['z']],
                            orientation=np.eye(3))
