import dataclasses
from abc import ABC, abstractmethod
from typing import Union

import control
import numpy as np

from . import spaces as sp
from .world import WorldObject
from ..core.scheduling import ScheduledObject, Action


@dataclasses.dataclass
class DynamicsSpaces:
    state_space: sp.Space = None
    input_space: sp.Space = None
    output_space: sp.Space = None


class Dynamics(ScheduledObject):
    state_space: sp.Space
    input_space: sp.Space
    output_space: sp.Space
    state: sp.State
    input: sp.State
    output: sp.State
    Ts: float
    state_initial: sp.State

    # === INIT =========================================================================================================
    def __init__(self, input_space: sp.Space = None, output_space: sp.Space = None, state_space: sp.Space = None,
                 Ts: float = None, state: Union[sp.State, list] = None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        update_action = Action(function=self.update, lambdas={'input': lambda: self.input})
        self.registerAction(update_action)

        if not hasattr(self, 'input_space'):
            self.input_space = input_space

        if not hasattr(self, 'state_space'):
            self.state_space = state_space

        if not hasattr(self, 'output_space'):
            self.output_space = output_space

        if state is None:
            state = self.state_space.getState()

        self.state = state
        self.input = self.input_space.getState()

        if Ts is not None:
            self.Ts = Ts  # TODO: or should this be taken from somewhere else?

    # === PROPERTIES ===================================================================================================
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = self.state_space.map(value)

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        self._input = self.input_space.map(value)

    @property
    def output(self):
        return self._output(self.state)

    @output.setter
    def output(self, value):
        raise Exception("Cannot set the output directly")

    # === METHODS ======================================================================================================
    def update(self, input=None):
        if input is not None:
            self.input = input
        self.state = self._dynamics(self.state, self.input)
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def reset(self):
        pass

    # === PRIVATE METHODS ==============================================================================================
    @abstractmethod
    def _dynamics(self, state: sp.State, input: sp.State):
        pass

    @abstractmethod
    def _output(self, state: sp.State):
        pass


# ======================================================================================================================
class LinearDynamics(Dynamics):
    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    sys: control.StateSpace
    sys_cont: control.StateSpace

    n: int
    p: int
    q: int

    def __init__(self, spaces: DynamicsSpaces = None, Ts: float = None, state: Union[sp.State, list] = None,
                 discrete: bool = False, *args,
                 **kwargs):
        super().__init__(spaces, Ts, state, *args, **kwargs)

        self.A = np.asarray(self.A)
        self.B = np.asarray(self.B)
        self.C = np.asarray(self.C)
        self.D = np.asarray(self.D)

        self.n = np.shape(self.A)[0]
        self.p = np.shape(self.B)[1]
        self.q = np.shape(self.C)[0]

        if not hasattr(self, 'discrete'):
            self.discrete = discrete

        self.sys = control.StateSpace(self.A, self.B, self.C, self.D, self.Ts, remove_useless_states=False)

    def _output(self, state: sp.State):
        pass

    def _dynamics(self, state: sp.State, input: sp.State):
        x = self.A @ state + self.B @ input
        return x

    def _init(self):
        pass


# ======================================================================================================================
class DynamicWorldObject(WorldObject, ABC):
    dynamics: Dynamics

    # === INIT =========================================================================================================
    def __init__(self, name, world, space: sp.Space, *args, **kwargs):
        super().__init__(name=name, world=world, space=space, *args, **kwargs)

        # Register the dynamics action in the World Dynamics Phase
        Action(name='dynamics', function=self.action_dynamics, object=self)

        self.registerChild(self.dynamics)

    # === PROPERTIES ===================================================================================================
    @property
    def state(self):
        return self.dynamics.state

    @state.setter
    def state(self, value):
        self.dynamics.state.set(value)

    @property
    def configuration(self):
        return self.space.map(self.dynamics.state)

    @configuration.setter
    def configuration(self, value):
        raise Exception("Cannot set configuration of dynamic world object. Set the state instead.")

    def setConfiguration(self, value, dimension=None, subdimension=None, space='local'):
        assert (space == 'local' or space == 'global' or space == self.space or space == self.space_global)

        config_temp = self.space.map(self._configuration)
        if dimension is None:
            config_temp = self.space.map(value)
        else:
            if subdimension is None:
                config_temp[dimension] = value
            else:
                config_temp[dimension][subdimension] = value

        self.state = self.dynamics.state_space.map(config_temp)
        self._updatePhysics(self.configuration)

    # === METHODS ======================================================================================================

    # === ACTIONS ======================================================================================================
    def action_dynamics(self, *args, **kwargs):
        self.dynamics.update()

    # === PRIVATE METHODS ==============================================================================================
