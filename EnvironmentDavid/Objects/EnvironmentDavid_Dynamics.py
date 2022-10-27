import math

import numpy as np

import scioi_py_core.core as core
from . import defs as defs

# ======================================================================================================================
# --- TankRobot

# Spaces
from scioi_py_core.core import spaces as sp

TankRobot_StateSpace = core.spaces.Space(dimensions=[
    core.spaces.Dimension(name='x'),
    core.spaces.Dimension(name='y'),
    core.spaces.Dimension(name='psi', limits=[0, 2 * math.pi], wrapping=True)
])

TankRobot_InputSpace = core.spaces.Space(dimensions=[
    core.spaces.Dimension(name='v'),
    core.spaces.Dimension(name='psi_dot'),
])

TankRobot_Spaces = core.dynamics.DynamicsSpaces()
TankRobot_Spaces.input_space = TankRobot_InputSpace
TankRobot_Spaces.state_space = TankRobot_StateSpace
TankRobot_Spaces.output_space = TankRobot_StateSpace


# Dynamics
class TankRobot_Dynamics(core.dynamics.Dynamics):
    spaces = TankRobot_Spaces
    Ts = defs.Ts

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _dynamics(self, state: sp.State, input: sp.State, *args, **kwargs):
        state['x'] = state['x'] + self.Ts * input['v'] * np.cos(state['psi'])
        state['y'] = state['y'] + self.Ts * input['v'] * np.sin(state['psi'])
        state['psi'] = state['psi'] + self.Ts * input['psi_dot']

        return state

    def _output(self, state: sp.State):
        output = self.spaces.output_space.zero()
        output['x'] = state['x']
        output['y'] = state['y']
        output['psi'] = state['psi']

    def _init(self, *args, **kwargs):
        pass
