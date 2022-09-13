import logging
import math
import random
import threading
import time

import numpy as np

from EnvironmentDavid.babylon import BABYLON_LiveBackend
from EnvironmentDavid.baseline.baseline_environment import TestbedVisualizationEnvironment
from EnvironmentDavid.mazes import maze_coop2
from EnvironmentDavid.baseline.robot_simulation import RobotSimulation
from scioi_py_core.utils.joystick.joystick_manager import JoystickManager

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d  %(levelname)-8s  %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def test(*args, **kwargs):
    print("HELLO")


loop_time = 40 / 1000

# ======================================================================================================================
# 1. Initialize hardware
# - Joysticks
jm = JoystickManager(required_sticks=1)
jm.joysticks[0].set_callback('button', 0, test, {})
# - HardwareManager
# - Optitrack

# 2. Load the environment
env = TestbedVisualizationEnvironment()
env.wallsFromList(maze_coop2)

robot_simulation = RobotSimulation(Ts=loop_time)

# 3. Convert the Environment to JSON
env.toJson(file="../babylon/objects.json")

# 4. Start the Webapp
webapp = BABYLON_LiveBackend("../babylon/example_LNDW_simple.html", options={})

cell_0 = env.getCell(0, 0)
robot_simulation.position = cell_0.floor_tile.center
env.robots['robot_01'].position = robot_simulation.position
env.robots['robot_01'].psi = robot_simulation.psi

last_collision_state = False


# ======================================================================================================================

def loop():
    global last_collision_state
    while True:
        time1 = time.perf_counter_ns()
        # -----------------------------------
        # 1. Read external hardware

        # 1.1 Joysticks
        v_js = -jm.joysticks[0].axis[1] * 400
        pd_js = -jm.joysticks[0].axis[2] * 4
        # 1.2 Optitrack -> Write robot states

        # 1.3 Hardware Manager

        # -----------------------------------
        # 2. Collision checking
        areas = env.collisionDetection(env.robots['robot_01'])

        if env.robots['robot_01'].collision and last_collision_state is False:
            jm.joysticks[0].rumble(strength=1, duration=0.25)

        last_collision_state = env.robots['robot_01'].collision

        # TODO: Put this into the robot class
        if 'front_left' in areas or 'front_right' in areas:
            if v_js > 0:
                v_js = 0

        if 'back_left' in areas or 'back_right' in areas:
            if v_js < 0:
                v_js = 0

        if 'left_front' in areas:
            if pd_js > 0:
                pd_js = 0

        if 'front_left' in areas and 'left_front' not in areas:
            if pd_js < 0:
                pd_js = 0

        if 'right_front' in areas:
            if pd_js < 0:
                pd_js = 0

        if 'front_right' in areas and 'right_front' not in areas:
            if pd_js > 0:
                pd_js = 0

        if 'left_back' in areas:
            if pd_js < 0:
                pd_js = 0

        if 'back_left' in areas and 'left_back' not in areas:
            if pd_js > 0:
                pd_js = 0

        if 'right_back' in areas:
            if pd_js > 0:
                pd_js = 0

        if 'back_right' in areas and 'right_back' not in areas:
            if pd_js < 0:
                pd_js = 0

        # if 'left_front' in areas or 'right_back' in areas or 'back_left' in areas or 'front_right' in areas:
        #     if pd_js > 0:
        #         pd_js = 0
        #
        # if 'left_back' in areas or 'right_front' in areas or 'front_left' in areas or 'back_right' in areas:
        #     if pd_js < 0:
        #         pd_js = 0

        # -----------------------------------
        # 3. Input calculation

        # -----------------------------------
        # 4. (Simulation of dynamics)
        robot_simulation.update([v_js, pd_js])
        env.robots['robot_01'].position = robot_simulation.position
        env.robots['robot_01'].psi = robot_simulation.psi
        # -----------------------------------
        # 5. Environment checking

        # -----------------------------------
        # 6. Visualization

        # DEBUG

        sample = env.generateSample()

        webapp.sendSample(sample)

        time2 = time.perf_counter_ns()

        sleep_time = (loop_time - ((time2 - time1) / 1e9))

        if sleep_time > 0:
            time.sleep(sleep_time)


def start_visualization():
    loop_thread = threading.Thread(target=loop, daemon=True)
    loop_thread.start()
    webapp.start()
