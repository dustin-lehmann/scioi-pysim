import logging
import math
import random
import threading
import time

from scioi_ritl.application.lndw.babylon import BABYLON_LiveBackend
from scioi_ritl.application.lndw.baseline.baseline_environment import BaselineEnvironment
from scioi_ritl.application.lndw.baseline.baseline_test import maze_left_vs
from scioi_ritl.application.lndw.baseline.robot_simulation import RobotSimulation


logging.basicConfig(
    format='%(asctime)s.%(msecs)03d  %(levelname)-8s  %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def test(*args, **kwargs):
    print("HELLO")


# ======================================================================================================================
# 1. Initialize hardware
# - Joysticks
# - HardwareManager
# - Optitrack

# 2. Load the environment
env = BaselineEnvironment()
env.wallsFromList(maze_left_vs)
# ======================================================================================================================

def loop():
    env.robots['robot_01'].position = [4000, 200]
    env.robots['robot_01'].psi = 0
    # -----------------------------------
    # 5. Environment checking
    time1 = time.perf_counter_ns()
    env.collisionDetection()
    time2 = time.perf_counter_ns()

    print((time2-time1)/1e6)

    # -----------------------------------
    # 6. Visualization

    # DEBUG


def main():
    loop()


if __name__ == '__main__':
    main()
