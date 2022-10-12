import logging
import math
import random
import threading
import time

import numpy as np

from scioi_ritl.application.lndw.babylon import BABYLON_LiveBackend
from scioi_ritl.application.lndw.baseline.baseline_environment import BaselineEnvironment_2
from scioi_ritl.application.lndw.baseline.baseline_test import maze_left_vs
from scioi_ritl.application.lndw.baseline.robot_simulation import RobotSimulation
from scioi_ritl.application.lndw.mazes import maze_coop
from scioi_ritl.extensions.joystick.joystick_manager import JoystickManager

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d  %(levelname)-8s  %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def test1(*args, **kwargs):
    jm.joysticks[0].rumble(0.8, 0.4)


def test2(*args, **kwargs):
    jm.joysticks[1].rumble(0.8, 0.4)


loop_time = 20 / 1000

# ======================================================================================================================
# 1. Initialize hardware
# - Joysticks
jm = JoystickManager(required_sticks=2)
jm.joysticks[0].set_callback('button', 0, test1, {})
jm.joysticks[1].set_callback('button', 0, test2, {})
# - HardwareManager
# - Optitrack

# 2. Load the environment
env = BaselineEnvironment_2()
env.wallsFromList(maze_coop)

env.robots['robot_01'].addSimulation(Ts=loop_time)
env.robots['robot_01'].joystick = jm.joysticks[0]
env.robots['robot_02'].addSimulation(Ts=loop_time)
env.robots['robot_02'].joystick = jm.joysticks[1]

# 3. Convert the Environment to JSON
env.toJson(file="../babylon/objects.json")

# 4. Start the Webapp
webapp = BABYLON_LiveBackend("../babylon/example_LNDW_simple.html", options={})

cell_1 = env.getCell(8, 12)
cell_2 = env.getCell(9, 12)

env.robots['robot_01'].position = cell_1.floor_tile.center
env.robots['robot_01'].psi = 0

env.robots['robot_02'].position = cell_2.floor_tile.center
env.robots['robot_02'].psi = 0


# ======================================================================================================================
def loop():
    while True:
        time1 = time.perf_counter_ns()
        # -----------------------------------
        # 1. Read external hardware

        # 1.1 Joysticks
        v1_js = -env.robots['robot_01'].joystick.axis[1] * 400
        pd1_js = -env.robots['robot_01'].joystick.axis[2] * 4

        v2_js = -env.robots['robot_02'].joystick.axis[1] * 400
        pd2_js = -env.robots['robot_02'].joystick.axis[2] * 4

        env.collisionDetection()

        input_1 = env.robots['robot_01'].calcInput(v1_js, pd1_js)
        input_2 = env.robots['robot_02'].calcInput(v2_js, pd2_js)

        env.robots['robot_01'].updateSimulation(input_1)
        env.robots['robot_02'].updateSimulation(input_2)

        sample = env.generate_sample()
        # -----------------------------------
        # 6. Visualization

        # DEBUG

        webapp.sendSample(sample)

        time2 = time.perf_counter_ns()

        sleep_time = (loop_time - ((time2 - time1) / 1e9))

        if sleep_time > 0:
            time.sleep(sleep_time)


def main():
    loop_thread = threading.Thread(target=loop, daemon=True)
    loop_thread.start()
    webapp.start()


if __name__ == '__main__':
    main()
