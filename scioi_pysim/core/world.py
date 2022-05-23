from typing import List, Union
from collections.abc import Iterable
import dataclasses

from . import simulation
from . import spaces
from . import agents


# WorldObject ##########################################################################################################
class WorldObject(simulation.SimObject):
    _object_id: int  # world ID
    world: 'World'  # World the object is assigned to
    name: str  # Trivial name

    # == INIT ==========================================================================================================
    def __init__(self, world: 'World' = None, name: str = None, Ts: float = -1):
        super().__init__(Ts)
        self.name = name
        self._object_id = None
        self.world = None

        if world is not None:
            if self.world is not world:
                if hasattr(world, 'add_object'):
                    world.add_object(self)


# World ################################################################################################################
class World(simulation.SimObject):

    # == INIT ==========================================================================================================
    def __init__(self, Ts: float = -1):
        super().__init__(Ts)

    # == PROPERTIES ====================================================================================================

    # == METHODS =======================================================================================================


# DynamicWorldObjectSpaces #############################################################################################
@dataclasses.dataclass
class DynamicWorldObjectSpaces:
    configuration_space: spaces.StateSpace = None


# DynamicWorldObject ###################################################################################################
class DynamicWorldObject(WorldObject):
    _spaces: DynamicWorldObjectSpaces
    config: spaces.State
    repr: 'PhysicalRepresentation'

    # == INIT ==========================================================================================================
    def __init__(self, configuration_space: spaces.StateSpace = None, config: spaces.State = None,
                 world: 'World' = None, name: str = None, Ts: float = -1):

        if not (hasattr(self, '_spaces')):
            self._spaces = DynamicWorldObjectSpaces()

        self._spaces.configuration_space = configuration_space
        self.config = config
        super().__init__(world=world, name=name, Ts=Ts)

    # == PROPERTIES ====================================================================================================
    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        if value is not None:
            self._config = self._spaces.configuration_space.map(value)
        else:
            self._config = None

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def coordinates(self):
        return 0

    # ------------------------------------------------------------------------------------------------------------------
    # def __deepcopy__(self, memodict={}):
    #     new_object = DynamicWorldObject(configuration_space=)


# DynamicWorldObjects ##################################################################################################
@dataclasses.dataclass
class DynamicWorldObjects:
    agents: List['Agent'] = dataclasses.field(default_factory=list)
    obstacles: List['Obstacle'] = dataclasses.field(default_factory=list)
    goals: List['Goal'] = dataclasses.field(default_factory=list)
    markers: List['Marker'] = dataclasses.field(default_factory=list)
    networks: List['Network'] = dataclasses.field(default_factory=list)

    def exists(self, object):
        if object in self.agents:
            return True
        if object in self.obstacles:
            return True
        if object in self.goals:
            return True
        if object in self.markers:
            return True
        if object in self.networks:
            return True
        return False


# DynamicWorld #########################################################################################################
class DynamicWorld(World):
    objects: DynamicWorldObjects

    coordinate_space: spaces.StateSpace
    sb_configuration_space: spaces.StateSpace

    # == INIT ==========================================================================================================
    def __init__(self, coordinate_space: spaces.StateSpace, configuration_space: spaces.StateSpace = None,
                 Ts: float = -1):
        super().__init__(Ts)

        self.coordinate_space = coordinate_space
        if configuration_space is None:
            self.configuration_space = self.coordinate_space
        else:
            self.configuration_space = configuration_space

        self.objects = DynamicWorldObjects()

        # --- Simulation Actions ---
        self.sim.actions['input'] = simulation.Phase(position=0, action=self._action_input)
        self.sim.actions['p1'] = simulation.Phase(position=1, action=self._action_p1)
        self.sim.actions['agents_predyn'] = simulation.Phase(position=2, action=self._action_agents_predyn)
        self.sim.actions['environment'] = simulation.Phase(position=3, action=self._action_environment)
        self.sim.actions['agents_postdyn'] = simulation.Phase(position=4, action=self._action_agents_postdyn)
        self.sim.actions['p2'] = simulation.Phase(position=5, action=self._action_p2)
        self.sim.actions['post'] = simulation.Phase(position=6, action=self._action_post)

    # == PROPERTIES ====================================================================================================

    # == METHODS =======================================================================================================
    def add_object(self, obj):
        if not isinstance(obj, list):
            obj = [obj]

        for o in obj:
            assert (isinstance(o, DynamicWorldObject))

            if self.objects.exists(o):
                continue

            # Register the simulation object
            self._register_child(o)

            o.world = self

            # Check the configuration space. If the object has none, assign it the full configuration space of the world
            if o._spaces.configuration_space is not None:
                assert (self.configuration_space.has_mapping(o._spaces.configuration_space))
            else:
                o._spaces.configuration_space = self.configuration_space

            # Add the object into the respective array
            if isinstance(o, agents.Agent):
                # Check if the agent's state space has a mapping into the configuration space
                assert (o._spaces.state_space.has_mapping(o._spaces.configuration_space))
                self.objects.agents.append(o)
            else:
                raise Exception("Not implemented yet")

    # ------------------------------------------------------------------------------------------------------------------
    def remove_object(self, obj):
        if not isinstance(obj, list):
            obj = [obj]

        for o in obj:
            self._deregister_child(o)
            if isinstance(o, agents.Agent):
                self.objects.agents.remove(o)

    # == PRIVATE METHODS ===============================================================================================

    def _action_input(self):
        pass

    def _action_p1(self):
        pass

    def _action_agents_predyn(self):
        phases_predyn = ['input', 'sensors', 'comm_pre_dyn', 'logic_pre_dyn', 'dynamics']
        for phase in phases_predyn:
            for agent in self.objects.agents:
                agent.sim.actions[phase].run()

    def _action_environment(self):
        pass

    def _action_agents_postdyn(self):
        phases_predyn = ['comm_post_dyn', 'logic_post_dyn', 'post']
        for phase in phases_predyn:
            for agent in self.objects.agents:
                agent.sim.actions[phase].run()

    def _action_p2(self):
        pass

    def _action_network(self):
        pass

    def _action_post(self):
        pass
