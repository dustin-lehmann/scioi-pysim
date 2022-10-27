import copy
import json
import time
from math import pi

from EnvironmentDustin.Environment.Environments.Environment_SingleTWIPR import Environment_SingleTWIPR
from scioi_py_core.objects.world import floor
from scioi_py_core.utils.orientations import rotmatFromPsi
import scioi_py_core.utils.world as world_utils
from scioi_py_core.visualization.babylon.babylon import BabylonVisualization


def main():
    env = Environment_SingleTWIPR()
    env.world.setSize(x=[-2, 2], y=[0, 4])
    env.obstacle1.configuration['pos'] = [10, 10, 10]

    config = {
        'world': env.world.getDefinition()
    }

    vis = BabylonVisualization(environment_config=config)
    vis.start()

    while True:
        time.sleep(1)


# TODO: Implement the translate and rotate functions. Also make some objects fixed so that changing
#  any in their config gives an error

if __name__ == '__main__':
    main()
