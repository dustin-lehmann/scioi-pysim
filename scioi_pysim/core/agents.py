import warnings
import typing
import dataclasses
import copy as cp

from . import world as wrld
from . import spaces
from . import dynamics as dyn
from scioi_pysim import core


# AgentSpaces ##########################################################################################################
@dataclasses.dataclass
class AgentSpaces(wrld.DynamicWorldObjectSpaces):
    state_space: spaces.StateSpace = None


# Agent ################################################################################################################
class Agent(wrld.WorldObject):
    _spaces: AgentSpaces
    state: spaces.State

    # == INIT ==========================================================================================================
    def __init__(self, state_space: spaces.StateSpace = None, state: spaces.State = None, world: wrld.World = None,
                 name: str = None, Ts: float = -1):

        if not(hasattr(self, '_spaces')):
            self._spaces = AgentSpaces()

        super().__init__(name=name, Ts=Ts, world=world)

        if state_space is not None:
            self._spaces.state_space = state_space
        if state_space is not None and state is None:
            self.state = state_space.zeros()
        if state_space is None and state is not None:
            self.state = state

    # == PROPERTIES ====================================================================================================
    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if self._spaces.state_space is not None:
            self._state = self._spaces.state_space.map(state)
        else:
            self._state = state

    # == METHODS =======================================================================================================

    # == PRIVATE METHODS ===============================================================================================


# DynamicAgent #########################################################################################################
@dataclasses.dataclass
class DynamicAgentSpaces(wrld.DynamicWorldObjectSpaces):
    dynamic_input_space: spaces.StateSpace = None
    external_input_space: spaces.StateSpace = None
    state_space: spaces.StateSpace = None


# DynamicAgent #########################################################################################################
class DynamicAgent(wrld.DynamicWorldObject, Agent):
    # Dynamics
    dynamics: core.dynamics.Dynamics
    input: spaces.State

    _spaces: DynamicAgentSpaces
    _dynamic_input: spaces.State
    external_input: spaces.State

    user_id: int  # user identifier

    # == INIT ==========================================================================================================
    def __init__(self, dynamics: typing.Union[core.dynamics.Dynamics, type],
                 configuration_space: spaces.StateSpace = None,
                 config: spaces.State = None,
                 state_space: spaces.StateSpace = None,
                 state: typing.Union[spaces.State, list] = None,
                 world: wrld.World = None,
                 external_input_space: spaces.StateSpace = None,
                 name: str = None,
                 user_id: int = None,
                 Ts: float = -1,
                 **kwargs):

        # --- Init of variables ---
        if not hasattr(self, '_spaces'):
            self._spaces = DynamicAgentSpaces()

        # --- Input Handling ---
        if state_space is None:
            self._spaces.state_space = dynamics.state_space
            self._state_equals_dynamics = True
        else:
            self._spaces.state_space = state_space
            self._state_equals_dynamics = False

        self._spaces.external_input_space = external_input_space
        self._external_input = None

        self.user_id = user_id

        wrld.DynamicWorldObject.__init__(self, configuration_space=configuration_space, config=config,
                                         world=world, name=name, Ts=Ts)


        if dynamics is None:
            raise Exception("TODO")
        else:
            if isinstance(dynamics, type) and issubclass(dynamics, core.dynamics.Dynamics):
                self.dynamics = dynamics()
            elif isinstance(dynamics, core.dynamics.Dynamics):
                self.dynamics = dynamics
            self._register_child(self.dynamics)  # Register the dynamics as a child SimObject

        # --- Super Classes ---
        # Agent.__init__(self, state_space=state_space, state=None, world=world, name=name, Ts=Ts)

        if state is not None:
            self.state = state
        else:
            self.state = None

        # --- Simulation Actions ---
        self.sim.actions['input'] = core.simulation.Phase(position=0,
                                                          action=core.simulation.Function(self._action_input,
                                                                                          position=10))
        self.sim.actions['sensors'] = core.simulation.Phase(position=1,
                                                            action=core.simulation.Function(self._action_sensors,
                                                                                            position=10))
        self.sim.actions['comm_pre_dyn'] = core.simulation.Phase(position=2,
                                                                 action=core.simulation.Function(
                                                                     self._action_comm_pre_dyn,
                                                                     position=10))
        self.sim.actions['logic_pre_dyn'] = core.simulation.Phase(position=3, action=core.simulation.Function(
            self._action_logic_pre_dyn,
            position=10))
        self.sim.actions['dynamics'] = core.simulation.Phase(position=4,
                                                             action=core.simulation.Function(self.dynamics.update,
                                                                                             lambdas={'input':
                                                                                                          lambda: self._dynamic_input}))
        self.sim.actions['comm_post_dyn'] = core.simulation.Phase(position=5, action=core.simulation.Function(
            self._action_comm_post_dyn,
            position=10))
        self.sim.actions['logic_post_dyn'] = core.simulation.Phase(position=6, action=core.simulation.Function(
            self._action_logic_post_dyn,
            position=10))
        self.sim.actions['post'] = core.simulation.Phase(position=7, action=core.simulation.Function(self._action_post,
                                                                                                     position=10))

    # == PROPERTIES ====================================================================================================
    @property
    def state(self):
        if not self._state_equals_dynamics:
            return self._state
        else:
            return self.dynamics.state

    @state.setter
    def state(self, value):
        if not self._state_equals_dynamics:
            self._state = self._spaces.state_space.map(value)
        else:
            self.dynamics.state = value

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def config(self):
        return self._spaces.configuration_space.map(self.state)

    @config.setter
    def config(self, value):
        if value is not None and self._spaces.configuration_space is not None:
            self.state = self._spaces.configuration_space.map(value)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def _dynamic_input(self):
        return self.dynamics.input

    @_dynamic_input.setter
    def _dynamic_input(self, value):
        self.dynamics.input = value

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def external_input(self):
        return self._external_input

    @external_input.setter
    def external_input(self, value):
        if self._spaces.external_input_space is not None:
            self._external_input = self._spaces.external_input_space.map(value, force=True)
        else:
            self._external_input = value

    # == METHODS =======================================================================================================
    def update(self, input=None, phase=None):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def simulate(self, input, x0=None, t0=None):
        x, y, u = self.dynamics.simulate(input, x0, t0)

        return x, y, u

    # ------------------------------------------------------------------------------------------------------------------
    def set_dynamic_input(self, input):
        self._dynamic_input = input

    # == PRIVATE METHODS ===============================================================================================

    def _action_input(self, *args, **kwargs):
        pass

    def _action_comm_pre_dyn(self):
        pass

    def _action_logic_pre_dyn(self):
        pass

    def _action_dynamics(self):
        pass

    def _action_comm_post_dyn(self):
        pass

    def _action_logic_post_dyn(self):
        pass

    def _action_post(self):
        pass

    def _action_sensors(self):
        pass

    # ------------------------------------------------------------------------------------------------------------------
    def __copy__(self):
        return cp.deepcopy(self)
    # def __deepcopy__(self, memodict={}):
    #     pass
