import numpy as np
import control
import copy as cp
from typing import Callable, List, ClassVar
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
import warnings

from . import spaces
from . import simulation



# Constraint ###########################################################################################################
# - indicate a violation (always)
# - put the state to a fixed value
# - throw an error
# - introduce new dynamics like state['xdot'] = 0.8*state['xdot']
# - for this, it should be programmed like

# if self.input_constraint is not None:
#     for all input constraints:
#         self.input = constraint(self.input, self.state)
#         is_violated = constraint.violated(self.input, self.state)


# Dynamics #############################################################################################################
class Dynamics(simulation.SimObject):
    state_space: spaces.StateSpace
    state: spaces.State

    input_space: spaces.StateSpace
    input: spaces.State

    output_state: spaces.StateSpace
    output: spaces.State

    n: int
    p: int
    q: int

    # == INIT ==========================================================================================================
    def __init__(self, Ts: float = -1, state_space: spaces.StateSpace = None, state: spaces.State = None,
                 input_space: spaces.StateSpace = None, output_space: spaces.StateSpace = None):
        super(Dynamics, self).__init__(Ts)

        if not hasattr(self, 'state_space') or self.state_space is None:
            if state_space is None:
                self.state_space = spaces.StateSpace(dof=self.n)
            else:
                self.state_space = state_space

        if not hasattr(self, 'input_space') or self.input_space is None:
            if input_space is None:
                self.input_space = spaces.StateSpace(dof=self.p)
            else:
                self.input_space = input_space

        if not hasattr(self, 'output_space') or self.output_space is None:
            if output_space is None:
                self.output_space = spaces.StateSpace(dof=self.q)
            else:
                self.output_space = output_space

        spaces.SpaceMapping(space_from=self.state_space, space_to=self.output_space, mapping=self._output_function,
                            inverse=None)

        if state is None:
            self.state = self.state_space.zeros()
        else:
            self.state = state

        self.input = self.input_space.zeros()

        # --- Simulation Action ---
        self.sim.actions['sim'] = simulation.Function(self.update, position=1)

    # == PROPERTIES ====================================================================================================
    @property
    def Ts(self):
        return self.sim.Ts

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = self.state_space.map(state)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, val):
        self._input = self.input_space.map(val)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def output(self):
        return self.output_space.map(self.state)

    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------

    # == METHODS =======================================================================================================
    def update(self, input):
        self._update()

        # map the input
        self.input = self.input_space.map(input)
        self.state = self._dynamics(self.state, self.input)

    # ------------------------------------------------------------------------------------------------------------------
    def simulate(self, input, x0=None, t0=None):
        # warnings.warn("This has to be correctly implemented")
        dynamic_input = []

        if isinstance(input, np.ndarray):
            assert (np.shape(input) == (self.p,))
            dynamic_input.append(input)
        elif isinstance(input, list):
            if len(input) == self.p and all(isinstance(elem, (int, float)) for elem in input):
                dynamic_input.append(input)
            elif self.p == 1 and all(isinstance(elem, (int, float)) for elem in input):
                dynamic_input = [np.atleast_1d(np.asarray(elem)) for elem in input]
            elif all(isinstance(elem, np.ndarray) for elem in input) and all(
                    np.shape(elem) == (self.p,) for elem in input):
                dynamic_input = input
            elif all(isinstance(elem, list) for elem in input) and all(len(elem) == self.p for elem in input):
                dynamic_input = [np.asarray(elem) for elem in input]
            else:
                raise Exception("Wrong data type for input u")
        elif isinstance(input, (int, float)) and self.p == 1:
            dynamic_input.append(np.atleast_1d(np.asarray(input)))
        elif isinstance(input, simulation.Timeseries):
            dynamic_input = input.data
        elif isinstance(input, spaces.State):
            assert (len(input) == self.input_space.dof)
            dynamic_input.append(input)
        else:
            raise Exception("Wrong data type for input u")

        if x0 is not None:
            self.state = x0

        assert (self.state is not None)

        x = simulation.Timeseries(Ts=self.sim.Ts)
        y = simulation.Timeseries(Ts=self.sim.Ts)
        u = simulation.Timeseries(Ts=self.sim.Ts)

        if t0:
            x.append(self.state)
            y.append(self.output)

        for i, u_k in enumerate(dynamic_input):
            self.state = self._dynamics(self.state, u_k)

            x.append(self.state)
            y.append(self.output)
            u.append(u_k)

        return x, y, u

    # == PRIVATE METHODS ===============================================================================================
    @abstractmethod
    def _dynamics(self, state, input):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    @abstractmethod
    def _output_function(self, state):
        pass

    # ------------------------------------------------------------------------------------------------------------------


# LinearDynamics #######################################################################################################
class LinearDynamics(Dynamics):
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    type: str

    sys: control.StateSpace
    sys_cont: control.StateSpace

    # == INIT ==========================================================================================================
    def __init__(self, type: str, state_space=None, state=None, Ts: float = -1):
        assert (type == 'cont' or type == 'discrete')

        if state_space is not None:
            self.state_space = state_space

        self.type = type
        self.A = np.asarray(self.A)
        self.B = np.asarray(self.B)
        self.C = np.asarray(self.C)
        self.D = np.asarray(self.D)

        self.n = np.shape(self.A)[0]
        self.p = np.shape(self.B)[1]
        self.q = np.shape(self.C)[0]

        super(LinearDynamics, self).__init__(Ts=Ts, state=state)

        if self.type == 'cont':
            self.sys = control.StateSpace(self.A, self.B, self.C, self.D, remove_useless=False)
        elif self.type == 'discrete':
            self.sys = control.StateSpace(self.A, self.B, self.C, self.D, self.Ts, remove_useless_states=False)

    # == PRIVATE METHODS ===============================================================================================
    def _dynamics(self, state, input):
        x = None
        if isinstance(input, (int, float)):
            input = np.atleast_1d(input)
        if self.type == 'cont':
            state_dot = self.A @ state + self.B @ input
            x = state + self.Ts * state_dot
        elif self.type == 'discrete':
            x = self.A @ state + self.B @ input
        return x

    # ------------------------------------------------------------------------------------------------------------------
    def _output_function(self, state):
        return self.C @ state
