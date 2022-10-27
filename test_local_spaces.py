import logging
from math import pi

import numpy as np

import scioi_py_core.core as core
import scioi_py_core.utils.orientations as orientations
import scioi_py_core.utils.world as world_utils

logging.basicConfig(level='INFO')

s1 = core.spaces.Space2D()
s2 = core.spaces.Space2D(parent=s1, origin=[[1, 1], pi / 2])


class TestObject(core.world.WorldObject):

    def _getParameters(self):
        pass

    def _updatePhysics(self, config, *args, **kwargs):
        pass


def example_local_space():
    world = core.world.World(space=s1)

    group1 = core.world.WorldObjectGroup(name='Group1', local_space=core.spaces.Space2D(), world=world)
    group1.configuration = [[1, 1], pi / 2]
    object1 = TestObject(world=world, group=group1)
    object1.configuration['pos']['x'] = 3



    pass


if __name__ == '__main__':
    example_local_space()
