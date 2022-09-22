import dataclasses
from abc import ABC, abstractmethod
from typing import Union

from . import spaces as sp
from .world import WorldObject
from ..core.scheduling import ScheduledObject, Action


@dataclasses.dataclass
class DynamicsSpaces:
    state_space: sp.Space = None
    input_space: sp.Space = None
    output_space: sp.Space = None


class Dynamics(ScheduledObject):
    spaces: DynamicsSpaces
    state: sp.State
    input: sp.State
    output: sp.State
    Ts: float
    state_initial: sp.State

    # === INIT =========================================================================================================
    def __init__(self, spaces: DynamicsSpaces = None, Ts: float = None, state: Union[sp.State, list] = None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        update_action = Action(function=self.update, lambdas={'input': lambda: self.input})
        self.registerAction(update_action)

        if spaces is not None:
            self.spaces = spaces

        if state is None:
            state = self.spaces.state_space.zeros()

        self.state = state
        self.input = self.spaces.input_space.zeros()

        if Ts is not None:
            self.Ts = Ts  # TODO: or should this be taken from somewhere else?

    # === PROPERTIES ===================================================================================================
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = self.spaces.state_space.map(value)

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        self._input = self.spaces.input_space.map(value)

    @property
    def output(self):
        return self._output(self.state)

    @output.setter
    def output(self, value):
        raise Exception("Cannot set the output directly")

    # === METHODS ======================================================================================================
    def update(self, input: sp.State = None):
        if input is not None:
            self.input = input
        self.state = self._dynamics(self.state, self.input)

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
    def _output(self, state: sp.State):
        pass

    def _dynamics(self, state: sp.State, input: sp.State):
        pass


# ======================================================================================================================
@dataclasses.dataclass
class DynamicWorldObjectSpaces:
    state_space: sp.Space = None
    input_space: sp.Space = None
    output_space: sp.Space = None
    config_space: sp.Space = None
    map_statespace_to_configspace: sp.Mapping = None

class DynamicWorldObject(WorldObject, ABC):
    dynamics: Dynamics
    spaces: DynamicWorldObjectSpaces

    # === INIT =========================================================================================================
    def __init__(self, name, world, *args, **kwargs):
        super().__init__(*args, **kwargs, name=name)

        # Register the dynamics action in the World Dynamics Phase
        Action(name='dynamics', function=self.action_dynamics, object=self)

        self.world = world
        self.world.addObject(self)
        self.registerChild(self.dynamics)

    # === PROPERTIES ===================================================================================================
    @property
    def configuration(self):
        return self.spaces.config_space.map(self.dynamics.state)

    @configuration.setter
    def configuration(self, value):
        raise Exception("Cannot set configuration of dynamic world object. Set the state instead.")

    # === METHODS ======================================================================================================

    # === ACTIONS ======================================================================================================
    def action_dynamics(self, *args, **kwargs):
        self.dynamics.update()

    # === PRIVATE METHODS ==============================================================================================
